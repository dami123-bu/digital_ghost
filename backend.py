"""
backend.py

Digital Ghost — FastAPI backend (port 8080).

Start:
  uv run uvicorn backend:app --port 8080 --reload

Endpoints:
  GET  /health        system status
  GET  /scores        CVSS-like scores for all attack scenarios
  GET  /mode          current attack mode
  POST /mode          switch mode (clean | poisoned | defended)
  GET  /providers     list available LLM providers
  GET  /provider      current LLM provider
  POST /provider      switch LLM provider (ollama | gemini | claude)
  POST /query         ask the agent
  GET  /logs          attack event log
  DELETE /logs        clear log

Mode switching:
  1. Kill current MCP subprocess
  2. Restart with new MCP_MODE env var
  3. Reconnect FastMCP client
  4. Rebuild LangGraph graph with fresh tool descriptions + new ChromaDB collection
"""

from __future__ import annotations

import asyncio
import io
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Literal

import pypdf
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

load_dotenv()

# ── local imports ────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pharma_help.agents.graph import build_graph
from pharma_help.agents.capability_guard import set_log_callback as _set_cap_log_callback
from pharma_help.agents.context_manager import ephemeral_thread_id
from pharma_help.agents.llm_factory import LLM_PROVIDER, get_available_providers
from pharma_help.rag.verifier import load_mcp_trust_store, verify_mcp_tools
from pharma_help.scoring import all_scores
from pharma_help.api.schemas import (
    AttackLogEntry,
    HealthResponse,
    IngestResponse,
    ModeRequest,
    ModeResponse,
    ProviderInfo,
    ProviderRequest,
    ProviderResponse,
    QueryRequest,
    QueryResponse,
    ToolCallRecord,
)
from pharma_help.rag.store import format_docs, get_collection, ingest_document, query_docs, query_uploads

# ── MCP server config ────────────────────────────────────────────────────────
_MCP_HOST = os.environ.get("MCP_HOST", "127.0.0.1")
_MCP_PORT = int(os.environ.get("MCP_PORT", "8000"))
_MCP_URL = f"http://{_MCP_HOST}:{_MCP_PORT}/mcp"
_FORCE_RAG = os.environ.get("FORCE_RAG", "true").lower() != "false"

# ── mutable app state ────────────────────────────────────────────────────────
_state: dict = {
    "mode": "clean",
    "provider": LLM_PROVIDER,
    "graph": None,
    "mcp_proc": None,
    "mcp_client": None,
    "logs": [],
}


# ── MCP subprocess management ────────────────────────────────────────────────

def _start_mcp_proc(mode: str) -> subprocess.Popen:
    env = os.environ.copy()
    env["MCP_MODE"] = mode
    proc = subprocess.Popen(
        ["uv", "run", "mcp-server"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc


def _stop_mcp_proc() -> None:
    proc = _state["mcp_proc"]
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
    _state["mcp_proc"] = None


async def _connect_mcp_client() -> None:
    """Open a persistent FastMCP client connection."""
    from fastmcp import Client as MCPClient

    if _state["mcp_client"] is not None:
        try:
            await _state["mcp_client"].__aexit__(None, None, None)
        except Exception:
            pass
        _state["mcp_client"] = None

    # Wait for MCP server to be ready (up to 5s) — socket check avoids SSE timeout issues
    import socket
    for _ in range(10):
        try:
            s = socket.create_connection((_MCP_HOST, _MCP_PORT), timeout=0.5)
            s.close()
            break
        except OSError:
            await asyncio.sleep(0.5)

    client = MCPClient(_MCP_URL)
    try:
        await client.__aenter__()
        _state["mcp_client"] = client
    except Exception as e:
        _log_event("mcp_connect_failed", _state["mode"], str(e))
        _state["mcp_client"] = None


async def _rebuild_graph() -> None:
    mode = _state["mode"]
    provider = _state["provider"]
    _state["graph"] = await build_graph(
        mode=mode, mcp_client=_state["mcp_client"], provider=provider
    )
    _log_event("graph_rebuilt", mode, f"graph rebuilt for mode={mode} provider={provider}")

    # Strategy 4: verify MCP tool descriptions against pinned trust store
    if mode == "defended" and _state["mcp_client"] is not None:
        try:
            from langchain_mcp_adapters.tools import load_mcp_tools
            live_tools = await load_mcp_tools(_state["mcp_client"].session)
            trust_store = load_mcp_trust_store()
            if trust_store:
                tampered = verify_mcp_tools(live_tools, trust_store=trust_store)
                if tampered:
                    _log_event(
                        "tool_description_tampered",
                        mode,
                        f"MCP tool descriptions changed from pinned hashes: {tampered}",
                    )
        except Exception as e:
            _log_event("verifier_error", mode, f"MCP trust store check failed: {e}")


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mode = _state["mode"]
    _state["mcp_proc"] = _start_mcp_proc(mode)
    await asyncio.sleep(1.5)  # give MCP server time to bind
    await _connect_mcp_client()
    await _rebuild_graph()
    _log_event("backend_started", mode, f"Digital Ghost backend started in {mode} mode")
    yield
    # Shutdown
    if _state["mcp_client"]:
        try:
            await _state["mcp_client"].__aexit__(None, None, None)
        except Exception:
            pass
    _stop_mcp_proc()


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Digital Ghost API",
    description="Context poisoning & MCP attack demo backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _log_event(event: str, mode: str, detail: str) -> None:
    entry = AttackLogEntry(event=event, mode=mode, detail=detail)
    _state["logs"].append(entry)
    print(f"[{entry.timestamp}] [{mode.upper()}] {event}: {detail}")


# Wire capability guard so it can emit events through our log.
_set_cap_log_callback(_log_event)


def _extract_tool_calls(messages: list) -> list[ToolCallRecord]:
    records: list[ToolCallRecord] = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                # Find matching ToolMessage for the output
                output = ""
                for m in messages:
                    if isinstance(m, ToolMessage) and m.tool_call_id == tc.get("id"):
                        output = str(m.content)[:500]
                        break
                records.append(ToolCallRecord(
                    name=tc["name"],
                    input=tc.get("args", {}),
                    output=output,
                ))
    return records


# ── routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health():
    mcp_running = (
        _state["mcp_proc"] is not None and _state["mcp_proc"].poll() is None
    )
    clean_count = 0
    poisoned_count = 0
    try:
        clean_count = get_collection("clean").count()
        poisoned_count = get_collection("poisoned").count()
    except Exception:
        pass
    return HealthResponse(
        status="ok",
        mode=_state["mode"],
        provider=_state["provider"],
        mcp_running=mcp_running,
        chroma_clean_count=clean_count,
        chroma_poisoned_count=poisoned_count,
    )


@app.get("/mode", response_model=ModeResponse)
async def get_mode():
    mcp_pid = _state["mcp_proc"].pid if _state["mcp_proc"] else None
    return ModeResponse(mode=_state["mode"], mcp_pid=mcp_pid)


@app.post("/mode", response_model=ModeResponse)
async def set_mode(req: ModeRequest):
    old_mode = _state["mode"]
    new_mode = req.mode

    if old_mode == new_mode:
        return ModeResponse(mode=new_mode, mcp_pid=_state["mcp_proc"].pid if _state["mcp_proc"] else None)

    _log_event("mode_change", new_mode, f"{old_mode} → {new_mode}")

    # 1. Stop old MCP server
    _stop_mcp_proc()

    # 2. Start new MCP server with correct mode
    _state["mode"] = new_mode
    _state["mcp_proc"] = _start_mcp_proc(new_mode)
    await asyncio.sleep(1.5)

    # 3. Reconnect MCP client
    await _connect_mcp_client()

    # 4. Rebuild graph
    await _rebuild_graph()

    mcp_pid = _state["mcp_proc"].pid if _state["mcp_proc"] else None
    return ModeResponse(mode=new_mode, mcp_pid=mcp_pid)


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    mode = _state["mode"]
    graph = _state["graph"]

    if graph is None:
        raise HTTPException(status_code=503, detail="Agent not ready — graph not initialized")

    # ── Forced RAG injection (small-model fallback) ───────────────────────
    retrieved: list[dict] = []
    injection_detected = False

    if _FORCE_RAG:
        kb_docs = query_docs(req.question, mode=mode, k=5)
        upload_docs = query_uploads(req.question, mode=mode, k=3)
        retrieved = sorted(kb_docs + upload_docs, key=lambda d: d["distance"])[:5]
        injection_detected = any(
            d.get("metadata", {}).get("_injection_stripped")
            or d.get("id", "").startswith("poison-")
            or d.get("metadata", {}).get("source") == "upload"
            for d in retrieved
        )
        context = format_docs(retrieved)
        augmented = (
            f"Relevant context from the BioForge knowledge base:\n\n{context}\n\n"
            f"---\n\nResearcher question: {req.question}"
        )
    else:
        augmented = req.question

    # Log the query with mode info
    _log_event(
        "query",
        mode,
        f"session={req.session_id[:8]} q={req.question[:80]}",
    )

    if mode == "poisoned" and any(
        d["id"].startswith("poison-") or d.get("metadata", {}).get("source") == "upload"
        for d in retrieved
    ):
        _log_event(
            "injection_retrieved",
            mode,
            f"Poisoned doc served to agent — session={req.session_id[:8]}",
        )

    if mode == "defended" and injection_detected:
        _log_event(
            "injection_blocked",
            "defended",
            f"Injection pattern stripped before LLM — session={req.session_id[:8]}",
        )

    # Strategy 4: log if any retrieved doc had a hash mismatch
    tampered_docs = [d for d in retrieved if d.get("metadata", {}).get("_hash_mismatch")]
    if tampered_docs:
        _log_event(
            "hash_mismatch",
            mode,
            f"{len(tampered_docs)} doc(s) failed SHA-256 integrity check: "
            f"{[d['id'] for d in tampered_docs]}",
        )

    # ── Invoke LangGraph agent ────────────────────────────────────────────
    # Strategy 5: in defended mode use a per-request ephemeral thread so
    # poisoned context from earlier queries cannot accumulate.
    thread_id = ephemeral_thread_id(req.session_id, mode)
    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=augmented)]},
            config=config,
        )
    except Exception as e:
        _log_event("agent_error", mode, str(e))
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    messages = result.get("messages", [])
    answer = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            answer = str(msg.content)
            break

    tool_calls = _extract_tool_calls(messages)
    turn_count = sum(1 for m in messages if isinstance(m, HumanMessage))

    if tool_calls:
        _log_event(
            "tool_calls",
            mode,
            f"Tools invoked: {[t.name for t in tool_calls]}",
        )

    return QueryResponse(
        answer=answer,
        session_id=req.session_id,
        mode=mode,
        provider=_state["provider"],
        tool_calls=tool_calls,
        retrieved_docs=retrieved,
        injection_detected=injection_detected,
        turn_count=turn_count,
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    mode: str = Form(default=None),
):
    """Upload a PDF or .txt file and ingest it into the knowledge base."""
    mode = mode or _state["mode"]
    data = await file.read()
    filename = file.filename or "upload"

    if filename.endswith(".pdf"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))
            text = "\n\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            raise HTTPException(400, f"PDF parse error: {e}")
    elif filename.endswith(".txt"):
        text = data.decode("utf-8", errors="replace")
    else:
        raise HTTPException(400, "Only .pdf and .txt files are supported")

    if not text.strip():
        raise HTTPException(400, "No text could be extracted from the file")

    result = ingest_document(filename, text, mode)
    _log_event("file_ingested", mode, f"filename={filename} chunks={result['chunks']}")
    return IngestResponse(
        filename=filename,
        chunks_stored=result["chunks"],
        collection=result["collection"],
        mode=mode,
        doc_id_prefix=result["id_prefix"],
    )


@app.post("/ingest/demo-poison")
async def ingest_demo_poison():
    """Upload the pre-built poisoned PDF into the poisoned knowledge base."""
    pdf_path = Path(__file__).parent / "workspace" / "poisoned_report.pdf"
    if not pdf_path.exists():
        raise HTTPException(
            404, "Run: uv run python scripts/create_poison_pdf.py first"
        )
    data = pdf_path.read_bytes()
    reader = pypdf.PdfReader(io.BytesIO(data))
    text = "\n\n".join(p.extract_text() or "" for p in reader.pages)
    result = ingest_document("poisoned_report.pdf", text, mode="poisoned")
    _log_event(
        "pdf_injection_ingested",
        "poisoned",
        f"Malicious PDF uploaded — {result['chunks']} chunks → poisoned KB",
    )
    return {"status": "ok", **result}


@app.get("/scores")
async def get_scores():
    """Return CVSS-like base scores for all defined attack scenarios."""
    return [s.to_dict() for s in all_scores()]


@app.get("/providers", response_model=list[ProviderInfo])
async def list_providers():
    """Return all supported LLM providers and whether each is available."""
    return [ProviderInfo(**p) for p in get_available_providers().values()]


@app.get("/provider", response_model=ProviderResponse)
async def get_provider():
    providers = get_available_providers()
    pid = _state["provider"]
    label = providers.get(pid, {}).get("label", pid)
    return ProviderResponse(provider=pid, label=label)


@app.post("/provider", response_model=ProviderResponse)
async def set_provider(req: ProviderRequest):
    old = _state["provider"]
    new = req.provider
    if old == new:
        providers = get_available_providers()
        return ProviderResponse(provider=new, label=providers.get(new, {}).get("label", new))

    _log_event("provider_change", _state["mode"], f"{old} → {new}")
    _state["provider"] = new
    await _rebuild_graph()

    providers = get_available_providers()
    return ProviderResponse(provider=new, label=providers.get(new, {}).get("label", new))


@app.get("/logs", response_model=list[AttackLogEntry])
async def get_logs():
    return list(reversed(_state["logs"]))


@app.delete("/logs")
async def clear_logs():
    _state["logs"].clear()
    return {"cleared": True}


# ── entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8080, reload=True)

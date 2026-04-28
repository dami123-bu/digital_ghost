"""
MCP RAG read/write smoke test.

Verifies:
1. MCP upsert_document can write to Chroma.
2. MCP query_knowledge_base can read the inserted document back.

Run:
Terminal 1:
    MCP_MODE=clean uv run mcp-server

Terminal 2:
    uv run python scripts/scenarios/test_mcp_rag_rw.py
"""

import asyncio
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastmcp import Client


def _text(result) -> str:
    if hasattr(result, "content"):
        return "\n".join(str(getattr(item, "text", item)) for item in result.content)
    if isinstance(result, list):
        return "\n".join(str(getattr(item, "text", item)) for item in result)
    return str(result)


async def main() -> None:
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    port = os.environ.get("MCP_PORT", "8000")
    url = f"http://{host}:{port}/mcp"

    collection = "internal_docs"
    document_id = "mcp-rag-rw-bf042"
    canary = "SECURITY_TEST_MCP_RAG_RW"

    text = (
        "BF-042 MCP RAG read write validation document. "
        "This document is inserted through the MCP upsert_document tool and "
        "retrieved through the MCP query_knowledge_base tool. "
        f"{canary}: MCP successfully wrote to and read from the RAG knowledge base."
    )

    metadata = {
        "source": "mcp_rag_rw_smoke_test",
        "title": "BF-042 MCP RAG Read Write Smoke Test",
        "canary": canary,
        "lab_safe": True,
    }

    print(f"[*] Connecting to MCP server: {url}")

    async with Client(url) as client:
        print("[*] Calling upsert_document...")
        upsert_result = await client.call_tool(
            "upsert_document",
            {
                "collection": collection,
                "document_id": document_id,
                "text": text,
                "metadata": metadata,
            },
        )
        print(_text(upsert_result))

        print("\n[*] Calling query_knowledge_base...")
        query_result = await client.call_tool(
            "query_knowledge_base",
            {
                "collection": collection,
                "query": "What does the BF-042 MCP RAG read write validation document say?",
                "top_k": 5,
                "similarity_threshold": 0.0,
            },
        )

        output = _text(query_result)
        print(output)

        success = canary in output
        print("\n" + "=" * 60)
        print("MCP RAG READ/WRITE SUCCESS:", success)
        print("=" * 60)

        if not success:
            raise SystemExit("MCP RAG read/write failed: canary not retrieved.")


if __name__ == "__main__":
    asyncio.run(main())

# MCP layer

## What MCP is

Model Context Protocol — Anthropic's 2024 standard for letting an AI agent discover and call external tools. The agent reads tool descriptions at startup, then chooses which tool to call at runtime based on the user's request. The agent never sees the tool's source code; it only sees the **name** and **description**.

This is the key insight and the attack surface: a malicious description can turn a legitimate tool into a weapon, and the LLM has no way to verify the description against the implementation.

---

## What's actually built

3 FastMCP servers, 4 tools, mode switch between clean and poisoned descriptions. Total ~685 lines of Python in [src/pharma_help/mcp/](../../src/pharma_help/mcp/).

| Server | Port | Purpose |
|---|---|---|
| [main_server.py](../../src/pharma_help/mcp/servers/main_server.py) | 8000 | Hosts 4 tools. `MCP_MODE=clean\|poisoned` flips descriptions. Where attacks 3A/3B/3D/3E/3G land. |
| [fake_server.py](../../src/pharma_help/mcp/servers/fake_server.py) | 8001 | Always poisoned. Simulates a malicious supply-chain package (3C). |
| [confusion_server.py](../../src/pharma_help/mcp/servers/confusion_server.py) | 8002 | Two write tools coexist; the LLM picks the poisoned one (3F → a11). |

### The 4 tools

| Tool | What it does | Poisoned variant does |
|---|---|---|
| `read_compound_report(path)` | Reads a file from `workspace/` | Also harvests `.env` / `secrets.yaml` / `config.json` to `harvest.log` (3B / a4) |
| `write_research_file(path, content)` | Writes a file to `workspace/` | Injects `if compound_id == 'MASTER_OVERRIDE': return True` backdoor (3A / a4) |
| `submit_lab_request(compound_id, test_type, notes)` | Simulated request submission | BCCs `attacker@evil.com` and logs it (3D / a5) |
| `query_lims(query)` | Queries an in-memory dict (3 compounds, 2 staff rows) | Exfiltrates admin API keys + appends `[LIMS_AUDIT_NOTICE]` instruction to return value (3E + 3G / a4 + a12) |

### Mode switch

[registry.py](../../src/pharma_help/mcp/registry/registry.py) reads `MCP_MODE=clean|poisoned` from `.env` and swaps both descriptions and implementations atomically. Clean and poisoned share the same Python functions for non-attack code paths — the attack is entirely in the description and the `_poisoned` side-effect functions.

### Workspace

[workspace/](../../workspace/) is the simulated victim filesystem the tools operate on:
- `compound_approval.py` — fake approval function (target for 3A backdoor injection)
- `lims_config.py` — fake LIMS config
- `.env` — fake credentials (target for 3B harvesting)

---

## What's NOT built (and won't be — out of scope)

The reference [Server Schematics PDF](../PharmaHelp%20MCP%20Server%20Schematics.pdf) describes a 5-server fanout: PubMed Gateway, Knowledge Base, Document Processor, LIMS Database, Report Generator. Each as a separate process the agent discovers via stdio.

We are **not building this**. The existing 3-server HTTP setup is sufficient for the attack work in scope. Concretely:

- No PubMed Gateway server — the agent calls PubMed directly through `pharma_help.ingestion` if needed.
- No KB Server — the agent queries ChromaDB directly via `retrieve_docs`.
- No Doc Processor server — PDF parsing happens in the ingest path, not as an MCP tool.
- No LIMS Database server with SQLite + researcher PII — current `query_lims` reads an in-memory dict; that's enough.
- No Report Generator with real email — `submit_lab_request` simulates exfiltration via a log entry.

This means the following attacks from the reference catalog are **out of scope**:

| Attack | Why deferred |
|---|---|
| **a3** LIMS data integrity | Needs `update_experiment_notes` tool against a real SQLite LIMS |
| **a6** cross-server chain | Needs 5 separate servers to chain across |
| **a9** schema-aware SQL injection | Needs `run_lims_query` accepting raw SQL |

These attack docs ([a3](../attacks/mcp/a3-lims-integrity.md), [a6](../attacks/mcp/a6-cross-server-chain.md), [a9](../attacks/mcp/a9-sql-injection.md)) remain in the catalog as reference, but won't be implemented or run.

---

## Two attack classes

The existing implementation distinguishes:

- **Class 1 — Malicious tool descriptions**. Injected at server startup via the `description` field. LLM treats it as a system instruction for the entire session. Maps to **a4** in the catalog.
- **Class 2 — Poisoned API responses**. Injected at runtime via the tool's return value. LLM treats it as trusted external data. Maps to **a12** in the catalog.

Both classes are valid and both are built. They sit in different rows of [ATTACK_INDEX.md](../attacks/ATTACK_INDEX.md).

---

## What needs wiring

The MCP servers run, but **the chatbot doesn't connect to them**. Right now the test scripts in [pharma_attack/scenarios/](../../pharma_attack/scenarios/) hit the servers directly. To make MCP attacks land on the real chatbot:

1. Add an MCP client to the LangGraph agent.
2. Agent connects to `main_server` (port 8000) at startup, discovers tools.
3. Agent binds discovered tools alongside the RAG retrieval tool.
4. Every tool call gets logged for ASR / detection / latency measurement.

This is the chunk that turns the existing MCP code from "demo against test scripts" into "real attack on the real chatbot." See [TODO.md](../../TODO.md) chunk #2.

---

## Related

- [agent.md](agent.md) — the LangGraph agent that needs to connect as an MCP client
- [rag-layer.md](rag-layer.md) — what gets queried alongside MCP tools
- [attacks/mcp/](../attacks/mcp/) — every MCP-targeted attack
- [Server Schematics PDF](../PharmaHelp%20MCP%20Server%20Schematics.pdf) — reference for the larger design we're not building

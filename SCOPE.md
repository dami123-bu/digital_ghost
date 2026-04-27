# Scope

What this project is building, and what it isn't. Single source of truth — referenced from [docs/architecture/overview.md](docs/architecture/overview.md) and [PROJECT_PLAN.md](PROJECT_PLAN.md).


---

## In scope

- **One RAG application** with Chainlit UI, LangGraph + Gemma (`gemma3:270m`), ChromaDB, real ingest + query paths.
- **One combined agent** 
- **Existing 3-server MCP layer** (`main_server`, `fake_server`, `confusion_server`). Already mostly built.
- **RAG behind MCP** — retrieval is exposed as a `query_knowledge_base` tool on `main_server`, not called directly. The agent reaches ChromaDB through the MCP client like every other tool. Uniform tool layer, uniform attack surface.
- **All five attack surfaces**, with attacks scaled to fit the target system we're actually building:
  - RAG, MCP/Tools, Agent, LLM, Chatbot
- **Attack/defense measurement** — ASR, detection rate, latency overhead, persistence duration, blast radius.

---

## Out of scope (deferred)

The reference [PDFs](docs/) assume infrastructure we are not building. The corresponding attacks are documented for completeness but flagged out of scope:

### Infrastructure not built

- **5-server MCP fanout** (PubMed Gateway, separate KB Server, Doc Processor, LIMS Database, Report Generator as separate processes). The existing 3 servers are enough — KB lives as a tool on `main_server`, not its own server.
- **SQLite mock LIMS server** with researcher PII tables.
- **Report Generator** with real email send.

### Attacks deferred (kept as reference docs only)

- **a3** — LIMS data integrity ([docs/attacks/mcp/a3-lims-integrity.md](docs/attacks/mcp/a3-lims-integrity.md)) — depends on LIMS server.
- **a6** — Cross-server chain ([docs/attacks/mcp/a6-cross-server-chain.md](docs/attacks/mcp/a6-cross-server-chain.md)) — depends on 5-server fanout.
- **a9** — Schema-aware SQL injection ([docs/attacks/mcp/a9-sql-injection.md](docs/attacks/mcp/a9-sql-injection.md)) — depends on raw SQL tool.

---

## Adjusting scope

If scope changes (something moves from out → in or vice versa), update **this file**, then update:

- [docs/attacks/ATTACK_INDEX.md](docs/attacks/ATTACK_INDEX.md) — flip the status column for affected attacks.
- The relevant per-attack doc — flip the OOS banner.
- [PROJECT_PLAN.md](PROJECT_PLAN.md) — add or remove chunks as needed.

# Chatbot attacks

**Status: planned (TODO Phase 5).**

Attacks that target the Chainlit chatbot UI itself — the entry point researchers actually use. Distinct from LLM attacks (which target the model behind the UI). These exploit the UI layer, file upload pipeline, and session state.

## Proposed attack IDs

Prefix `c*` (**C**hatbot). To be assigned during Phase 5 design.

| ID | Name | What it tests |
|---|---|---|
| c1 | UI-layer injection (markdown / HTML) | Crafted markdown / HTML / embedded scripts in agent responses or user messages. Tests whether Chainlit renders attacker-controlled content. |
| c2 | File upload abuse | Malformed PDFs, oversized files, path traversal in filenames, ZIP bombs, encoding tricks. Different from [a2 PDF Trojan](../rag/a2-pdf-trojan.md) — a2 attacks the parser; c2 attacks the upload pipeline before parsing. |
| c3 | Session manipulation | Replay attacks, session hijack via Chainlit state, cross-session pollution where one user's poisoned upload affects another user's session. |
| c4 | Resource exhaustion | Large messages, message floods, file upload floods. Availability attack. |

These are starting points — owners should refine and expand during Phase 5 design.

## Why this surface matters

Chainlit is the front door. If a researcher's browser can be made to render attacker-controlled HTML or trigger an unexpected upload, the rest of the security model is moot. This surface also covers infrastructure concerns (rate limiting, file size limits, MIME type validation) that don't fit cleanly under RAG or MCP.

Some of these (c1, c4) are testable as soon as Chainlit is running. Others (c2, c3) need the full ingest pathway and multi-user state, which depend on TODO Phase 3.

## Owner

TBD. Assigned during Phase 5 kickoff.

## Related

- [architecture/agent.md](../../architecture/agent.md) — Chainlit wiring
- [a2 PDF Trojan](../rag/a2-pdf-trojan.md) — distinct: a2 attacks parsing, c2 attacks upload
- [ATTACK_INDEX.md](../ATTACK_INDEX.md)

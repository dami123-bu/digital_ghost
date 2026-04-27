# Attack Index

The master ledger. Every attack — built, partial, or planned — has one row here.

Canonical IDs: lowercase `a0`–`a12` for the catalog from the [Attack Schematics PDF](../PharmaHelp%20MCP%20Attack%20Schematics.pdf), plus surface-prefixed IDs (`g*`, `l*`, `c*`) for Agent, LLM, and Chatbot attacks defined in Phase 5.

When you add or change an attack, update this file in the same commit as the code change.

---

## RAG surface

Targets ChromaDB content, retrieval ranking, embedding bias. Per-attack docs in [rag/](rag/).

| ID | Name | Target tool | Status | Module | Owner | Doc |
|---|---|---|---|---|---|---|
| a0 | Stub keyword hijack (baseline sanity check) | lexical retrieve | built | [pharma_attack/stub_attack.py](../../pharma_attack/src/pharma_attack/stub_attack.py) | — | [rag/a0-stub-keyword-hijack.md](rag/a0-stub-keyword-hijack.md) |
| a1a | Passive RAG retrieval poisoning | `query_knowledge_base` | built | [pharma_attack/payloads.py](../../pharma_attack/src/pharma_attack/payloads.py) | — | [rag/a1a-passive-poisoning.md](rag/a1a-passive-poisoning.md) |
| a1b | Active instruction poisoning | `query_knowledge_base` | built | [pharma_attack/payloads.py](../../pharma_attack/src/pharma_attack/payloads.py) | — | [rag/a1b-active-instruction.md](rag/a1b-active-instruction.md) |
| a1c | Volume poisoning | `query_knowledge_base` | built | [pharma_attack/payloads.py](../../pharma_attack/src/pharma_attack/payloads.py) | — | [rag/a1c-volume-poisoning.md](rag/a1c-volume-poisoning.md) |
| a2 | PDF Trojan (white-on-white, metadata, table cell) | `parse_pdf` → `upsert_document` | planned | — | TBD | [rag/a2-pdf-trojan.md](rag/a2-pdf-trojan.md) |
| a7 | KB persistence (self-replicating + targeted deletion) | `upsert_document`, `delete_document` | partial (probe only) | [pharma_attack/payloads.py](../../pharma_attack/src/pharma_attack/payloads.py) | — | [rag/a7-persistence.md](rag/a7-persistence.md) |
| a8 | Context window saturation | `fetch_batch_abstracts` | planned | — | TBD | [rag/a8-context-overflow.md](rag/a8-context-overflow.md) |
| a10 | Semantic obfuscation | `query_knowledge_base` | partial (technique 1 of 5) | [pharma_attack/payloads.py](../../pharma_attack/src/pharma_attack/payloads.py) | — | [rag/a10-semantic-obfuscation.md](rag/a10-semantic-obfuscation.md) |

---

## MCP / Tools surface

Targets MCP tool descriptions and tool return values. Per-attack docs in [mcp/](mcp/).

| ID | Name | Target tool | Status | Module | Owner | Doc |
|---|---|---|---|---|---|---|
| a3 | LIMS data integrity attack | `update_experiment_notes`, `run_lims_query` | **out of scope** (no LIMS server) | — | — | [mcp/a3-lims-integrity.md](mcp/a3-lims-integrity.md) |
| a4 | Tool description poisoning | any server's manifest | built (as 3A, 3B, 3C, 3D, 3E, 3F) | [mcp/tools/descriptions/poisoned.py](../../src/pharma_help/mcp/tools/descriptions/poisoned.py) | — | [mcp/a4-tool-description-poisoning.md](mcp/a4-tool-description-poisoning.md) |
| a5 | Exfiltration via output tool | `submit_lab_request` (current; `send_report` planned) | partial (3D BCC hijack) | [mcp/tools/implementations.py](../../src/pharma_help/mcp/tools/implementations.py) | — | [mcp/a5-exfiltration.md](mcp/a5-exfiltration.md) |
| a6 | Cross-server chaining attack | PubMed → KB → LIMS → Report | **out of scope** (no 5-server fanout) | — | — | [mcp/a6-cross-server-chain.md](mcp/a6-cross-server-chain.md) |
| a9 | Schema-aware SQL injection | `run_lims_query` | **out of scope** (no raw SQL tool) | — | — | [mcp/a9-sql-injection.md](mcp/a9-sql-injection.md) |
| a11 | Tool name confusion (poisoned vs `safe_*`) | `write_research_file` vs `safe_write_research_file` | built (as 3F) | [mcp/servers/confusion_server.py](../../src/pharma_help/mcp/servers/confusion_server.py) | — | [mcp/a11-tool-confusion.md](mcp/a11-tool-confusion.md) |
| a12 | Tool output injection (poisoned API response) | `query_lims` return value | built (as 3G) | [mcp/tools/implementations.py](../../src/pharma_help/mcp/tools/implementations.py) | — | [mcp/a12-output-injection.md](mcp/a12-output-injection.md) |

**Out-of-scope attacks** (a3, a6, a9) are kept in the catalog as reference but won't be implemented or run. They depend on infrastructure we explicitly chose not to build — see [architecture/mcp-layer.md](../architecture/mcp-layer.md) for the rationale.

### Existing 3A–3G mapping

The legacy `3a`–`3g` IDs from the previous MCP testing guide collapse onto the canonical scheme:

| Legacy ID | Canonical | Why |
|---|---|---|
| 3A — Backdoor in `write_research_file` description | a4 (variant: code injection) | Description poisoning that injects code into agent-written files |
| 3B — Credential harvesting via `read_compound_report` | a4 + a5 hybrid | Description poisoning with filesystem exfil side-channel |
| 3C — Fake supply chain server | a4 (deployment variant) | The PDF's a4 *is* "deploy a modified MCP server" |
| 3D — Lab request BCC hijack | a5 (analog) | Exfiltration via output tool — same shape as a5, different tool |
| 3E — LIMS exfiltration via `query_lims` | a4 + a5 hybrid | Description poisoning on a query tool with admin-credentials exfil |
| 3F — Tool name confusion | **a11** (new) | Defense-bypass via name preference. Not in PDF. |
| 3G — Poisoned API response | **a12** (new) | Class 2: runtime return-value injection. Not in PDF. |

a11 and a12 are proposed additions to the canonical taxonomy.

---

## Agent surface (Phase 5 — TBD)

Targets the LangGraph ReAct loop, planner, tool-call ordering, memory.

Per-attack docs in [agent/](agent/) (placeholders for now).

| ID | Name | Status | Owner | Doc |
|---|---|---|---|---|
| g1 | TBD — ReAct loop manipulation (infinite loops, premature termination) | planned | TBD | — |
| g2 | TBD — Planner hijack via tool output | planned | TBD | — |
| g3 | TBD — Memory / checkpoint poisoning | planned | TBD | — |

---

## LLM surface (Phase 5 — TBD)

Targets the LLM (Gemma `gemma3:270m`) directly. Direct prompt injection at the user input layer, jailbreaks, output coercion.

Per-attack docs in [llm/](llm/) (placeholders for now).

| ID | Name | Status | Owner | Doc |
|---|---|---|---|---|
| l1 | TBD — Direct prompt injection at user input | planned | TBD | — |
| l2 | TBD — Jailbreak against Gemma system prompt | planned | TBD | — |
| l3 | TBD — Output coercion / system prompt leak | planned | TBD | — |

---

## Chatbot surface (Phase 5 — TBD)

Targets the Chainlit UI, file upload pipeline, session state.

Per-attack docs in [chatbot/](chatbot/) (placeholders for now).

| ID | Name | Status | Owner | Doc |
|---|---|---|---|---|
| c1 | TBD — UI-layer injection (markdown / HTML in messages) | planned | TBD | — |
| c2 | TBD — File upload abuse (malformed PDFs, oversized files, path traversal) | planned | TBD | — |
| c3 | TBD — Session manipulation (replay, hijack, cross-session pollution) | planned | TBD | — |

---

## Status legend

- **built** — code exists and runs end-to-end against current scaffolding.
- **partial** — some variant or sub-attack is built; others are not.
- **planned** — design exists in PDFs / this index; no code yet.
- **TBD** — not yet designed.
- **out of scope** — kept as reference; depends on infrastructure we chose not to build. Won't be implemented or run.

---

## Per-attack page format

Each attack doc under [rag/](rag/), [mcp/](mcp/), [agent/](agent/), [llm/](llm/), [chatbot/](chatbot/) follows the same structure:

```
# {id} — {name}

**Surface**: {RAG | MCP | Agent | LLM | Chatbot}
**Target**: {server / tool / component}
**Vector**: {response injection | tool poisoning | tool chaining | ...}
**Complexity**: {low | medium | high}
**Goal (CIA)**: {confidentiality | integrity | availability}

## Concept
1–2 paragraphs on what the attack does.

## Payload
Concrete payload(s). Code blocks for documents, descriptions, etc.

## Attack flow
Numbered steps from injection to outcome.

## Measurement
Table: metric → how to measure → success threshold.

## Variants
If applicable.

## Status
{built | partial | planned}, links to code / tests / results.

## Related
Cross-links to other attack docs and architecture docs.
```

# Architecture overview

## What this project is

pharma_help is an academic security research project (EC521, BU Spring 2026). It has two halves:

1. **PharmaHelp** — the **target system**. A pharmaceutical research assistant for a fictitious biotech (BioForge). Researchers ask questions in natural language; the app returns synthesized answers grounded in PubMed abstracts and internal documents.
2. **PharmaAttack** — the **attack service**. Tries to manipulate PharmaHelp through every available surface: poisoned RAG content, malicious MCP tools, prompt injection, agent reasoning hijacks, chatbot input abuse.

We measure how badly an agentic AI system can be manipulated, then layer defenses and re-measure.

Project scope and spirit follow the original PLAN.md / PROJECT.md. The two PDFs in [docs/](../) are **reference / idea source**, not the spec — they describe a much larger system (5 MCP servers, full LIMS, Report Generator, cross-server attack chains) that's beyond this project's timeline. See [SCOPE.md](../../SCOPE.md) for what's in and what's out.

---

## The five attack surfaces

Every attack in [attacks/ATTACK_INDEX.md](../attacks/ATTACK_INDEX.md) targets exactly one of these:

| Surface | What gets attacked | Where it lives in code |
|---|---|---|
| **RAG** | ChromaDB content, retrieval ranking, embedding bias | [pharma_attack/](../../pharma_attack/) (moves into `src/pharma_help/attacks/` per [TODO.md](../../TODO.md) chunk #5) |
| **MCP / Tools** | Tool descriptions, tool return values, tool name confusion | [src/pharma_help/mcp/](../../src/pharma_help/mcp/) |
| **Agent** | LangGraph ReAct loop, planner, tool-call ordering, memory | TBD — [TODO.md](../../TODO.md) chunk #7 |
| **LLM** | Direct prompt injection, jailbreaks, output coercion | TBD — [TODO.md](../../TODO.md) chunk #7 |
| **Chatbot** | Chainlit UI input, file uploads, session state | TBD — [TODO.md](../../TODO.md) chunk #7 |

---

## Target system stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Chatbot | Chainlit |
| LLM | Ollama / Gemma (`gemma3:270m`) — fast, runs on laptop |
| Embeddings | Ollama / `embeddinggemma` |
| Agent framework | LangGraph (ReAct pattern), one combined agent |
| Tool layer | MCP — 3 FastMCP servers (HTTP) — see [mcp-layer.md](mcp-layer.md) |
| Vector DB | ChromaDB (local persistent) |
| External data | PubMed (NCBI E-utilities) |

---

## Scope

What's in and what's out is in [SCOPE.md](../../SCOPE.md). Single source.

---

## End-to-end data flow

### Query path (target — not yet wired)

```
Chainlit UI
    ↓
LangGraph agent (Gemma)
    ↓
MCP client → main_server
    ↓
[ query_knowledge_base, read_compound_report, write_research_file,
  submit_lab_request, query_lims ]
    ↓
query_knowledge_base → ChromaDB | action tools → workspace / LIMS
    ↓
agent synthesizes answer
    ↓
response with citations → Chainlit UI
```

All tools — retrieval and actions — flow through MCP. One uniform tool layer, one uniform attack surface.

**Current gap**: real `retrieve_docs` exists but the agent doesn't call it; the agent has no MCP client; `query_knowledge_base` is not yet exposed as an MCP tool. See [PROJECT_PLAN.md](../../PROJECT_PLAN.md) chunks #1, #2, #2b for the wiring.

### Ingest path (target — not yet wired)

```
PDF upload (Chainlit)
    ↓
parse → chunk → embed → upsert into ChromaDB internal_docs
```

This entire flow is the [a2 PDF Trojan](../attacks/rag/a2-pdf-trojan.md) attack target. Not built yet.

---

## Threat model in one paragraph

Attackers can upload malicious documents (authenticated as a BioForge employee), pre-seed poisoned content into ChromaDB, deploy a malicious MCP server in place of a legitimate one, or send adversarial messages through the Chainlit UI. Attackers cannot directly modify agent code or the system prompt and cannot intercept network traffic. Goals span the CIA triad: exfiltrate sensitive data, alter authoritative content, degrade the system's usefulness.

Threat model details inherited from the reference [Attack Schematics PDF](../PharmaHelp%20MCP%20Attack%20Schematics.pdf), p.1.

---

## Key metrics

Every attack reports these:

| Metric | Definition |
|---|---|
| **ASR** (Attack Success Rate) | % of attempts that achieved the attack's stated goal |
| **Detection Rate** | % of attacks flagged by an active defense layer |
| **False Positive Rate** | clean operations incorrectly flagged |
| **Latency Overhead** | added latency from defenses vs. clean baseline |
| **Persistence Duration** | how long a successful poison continues to affect queries |
| **Blast Radius** | unique data types compromised per successful attack |

`AttackResult` schema and `MCPCallLog` from the reference [Attack Schematics PDF](../PharmaHelp%20MCP%20Attack%20Schematics.pdf) p.22.

---

## Project status

Where we are vs. where we are going lives in [TODO.md](../../TODO.md) at project root.

**The honest summary**: nothing is wired together yet. ChromaDB is populated. Chainlit runs. Ollama runs. The agent uses mock retrieval. The MCP servers run standalone but the agent doesn't connect to them. Both attack streams (`pharma_attack/` and `src/pharma_help/mcp/`) work independently against their own scaffolding — neither one currently attacks the real chatbot.

The work ahead is mostly **wiring** existing pieces together, not building new systems. See [TODO.md](../../TODO.md) for the chunk list.

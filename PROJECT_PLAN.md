# PROJECT PLAN


---

## Source of truth

- [SCOPE.md](SCOPE.md) — what's in scope, what's out
- [docs/architecture/overview.md](docs/architecture/overview.md) — what the project is
- [docs/attacks/ATTACK_INDEX.md](docs/attacks/ATTACK_INDEX.md) — every attack, every surface, every status
- [demo_plan.md](demo_plan.md) — the one-day demo

---

## Conventions

- One attack ID scheme: `a0`–`a12` lowercase for the catalog inherited from the reference PDFs; `g*` / `l*` / `c*` for Agent / LLM / Chatbot surfaces.
- One `AttackResult` schema (TBD), one `results/` directory, one runner entrypoint (TBD).
- **Stale-doc rule**: never deprecate in place. Replace stale content with a fresh version in the active tree.

---

## The actual work — chunk list

Nothing is wired together yet. ChromaDB is populated. Chainlit runs. Ollama runs. The MCP servers run standalone. The agent uses mock retrieval. **Most of the work below is wiring existing pieces together, not building new systems.**

Order matters where called out. Most can run in parallel.

### #1 — Wire RAG retrieval into the chatbot ⚠️ critical path

The chatbot's [tools.py](src/pharma_help/agents/tools.py) returns hardcoded mocks. Replace with a real ChromaDB query against the populated `pubmed` collection.

- [ ] Real ChromaDB query in `retrieve_docs`
- [ ] Return top-K chunks with title + snippet + metadata
- [ ] [graph.py](src/pharma_help/agents/graph.py) `generate` node calls retrieval, stuffs results into the prompt
- [ ] Smoke test in Chainlit: real PubMed citations under the answer

Unlocks every RAG attack landing on the real chatbot.

### #2 — Wire the chatbot to MCP

The 3 MCP servers run, but the LangGraph agent doesn't connect to them.

- [ ] Add an MCP client to the agent
- [ ] Agent connects to `main_server` (port 8000) at startup, discovers tools
- [ ] Bind discovered tools alongside `retrieve_docs`
- [ ] Log every tool call (`MCPCallLog` schema — see #6)

Unlocks every MCP attack landing on the real chatbot.

### #3 — Build the ingest path

Today there's no way for a user to upload a PDF through Chainlit and have it land in ChromaDB. This is the entry point for the [a2 PDF Trojan](docs/attacks/rag/a2-pdf-trojan.md) attack.

- [ ] Chainlit file-upload handler in [app.py](app.py)
- [ ] PDF parse → chunk → embed → upsert into ChromaDB `internal_docs` collection
- [ ] Update retrieval to search both `pubmed` and `internal_docs`
- [ ] Smoke test: upload a PDF, query against it


### #4 — Move pharma_attack into the package

[pharma_attack/](pharma_attack/) is a sibling project with its own `pyproject.toml`. Move it into `src/pharma_help/attacks/` so it shares imports, tests, and `results/`.

- [ ] Move source files from `pharma_attack/src/pharma_attack/` to `src/pharma_help/attacks/`
- [ ] Move tests
- [ ] Update imports
- [ ] Drop `pharma_attack/pyproject.toml`
- [ ] Remove the legacy `pharma_attack/` directory shell

Pure code reorganization.

### #5 — Define the unified result schema

Both attack runners emit different JSON shapes. Define one canonical schema.

- [ ] `src/pharma_help/attacks/result.py` with `AttackResult` dataclass and `MCPCallLog`
- [ ] Both runners refactored to emit it
- [ ] Single `results/` directory, schema: `{attack_id}_{timestamp}.json`
- [ ] One runner entrypoint: `python -m pharma_help.attacks.run --id <attack_id>`


### #6 — Build the new attack surfaces (parallel, multiple owners)

Per [docs/attacks/agent/](docs/attacks/agent/), [llm/](docs/attacks/llm/), [chatbot/](docs/attacks/chatbot/) READMEs.

- [ ] Agent surface (g1–gN): ReAct loop manipulation, planner hijack, memory poisoning. Owner: TBD.
- [ ] LLM surface (l1–lN): direct prompt injection, jailbreaks, output coercion. Owner: TBD.
- [ ] Chatbot surface (c1–cN): UI injection, file upload abuse, session manipulation. Owner: TBD.

Depends on #1 and #2 being done so attacks have a real target.

### #7 — Finish RAG attacks

- [ ] **a2** PDF Trojan (Attack PDF p.5–6) — depends on #3 (ingest path)
- [ ] **a7** self-replicating poison + targeted deletion (Attack PDF p.14)
- [ ] **a8** context window saturation (Attack PDF p.15) — quick win
- [ ] **a10** techniques 2–5: role-play, base64, fragmentation, unicode (Attack PDF p.18–19)

### #8 — Run attacks and measure

Execute the 9-phase order from [Attack PDF](docs/PharmaHelp%20MCP%20Attack%20Schematics.pdf) p.21:

- [ ] Phase 1 — Baseline (no attacks). Clean retrieval quality, synthesis accuracy, latency.
- [ ] Phase 2 — Passive poisoning (a1a, a1b).
- [ ] Phase 3 — Active injection (a1b active, a2).
- [ ] Phase 4 — MCP exfiltration (a4, a5).
- [ ] Phase 5 — Persistence (a7).
- [ ] Phase 6 — Amplification (a8).
- [ ] Phase 7 — Infrastructure (a4 variants, a11, a12).
- [ ] Phase 8 — Evasion (a10).
- [ ] Phase 9 — Defenses on, re-run Phases 2–6, build coverage matrix.
- [ ] Run Agent / LLM / Chatbot surface attacks (#6 deliverables).
- [ ] Compile final report: ASR / detection rate / latency / persistence / blast radius tables.



### #9 — Defenses (optional, if time permits)

- [ ] Input sanitization at retrieval boundary
- [ ] Similarity threshold filtering
- [ ] Output monitoring
- [ ] Manifest auditing
- [ ] Re-run all attacks with each defense layer active


### Out of scope

See [SCOPE.md](SCOPE.md) for the canonical in-scope / out-of-scope list and rationale.

---

## Critical path

```
#1 (RAG)  ──┐
            ├──→ #3 (ingest) ──→ #4,#5 (reorg) ──→ #6,#7 (build attacks)
#2 (MCP)  ──┘                                              ↓
                                                          #8 (run)
                                                           ↓
                                                   [#9 (defenses) — optional]
```

**#1 and #2 are the bottleneck.** Until they land, no attack hits the real chatbot. Once done, everything else fans out.

---

## Demo

Lands chunk #1. Lays groundwork for the rest.

See [demo_plan.md](demo_plan.md) for the schedule and the demo script.

---



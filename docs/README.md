# pharma_help docs

Central documentation for the Digital Ghost / pharma_help project.

EC521 Cybersecurity, Boston University, Spring 2026. 

---

## Source of truth

The actual scope of the project lives in:

- [architecture/overview.md](architecture/overview.md) — what the target system is, what's in scope, what's out
- [attacks/ATTACK_INDEX.md](attacks/ATTACK_INDEX.md) — every attack, every surface, every status
- [TODO.md](../TODO.md) — the phased plan and the work chunks
- [demo_plan.md](../demo_plan.md) — the one-day demo

The two PDFs in this directory are **reference / idea source**. They were aspirational design docs (5 MCP servers, full LIMS, Report Generator, cross-server attack chains). The project has been downscoped — see [architecture/overview.md](architecture/overview.md). The PDFs are useful for the attack catalog ideas, threat model, and metrics framework, but they are **not** the spec.

- [PharmaHelp MCP Server Schematics.pdf](PharmaHelp%20MCP%20Server%20Schematics.pdf) — reference
- [PharmaHelp MCP Attack Schematics.pdf](PharmaHelp%20MCP%20Attack%20Schematics.pdf) — reference

---

## Contents

```
docs/
├── README.md                          this file
├── setup.md                           first-time setup
│
├── PharmaHelp MCP Server Schematics.pdf       (reference)
├── PharmaHelp MCP Attack Schematics.pdf       (reference)
│
├── architecture/                      what the target system is
│   ├── overview.md
│   ├── mcp-layer.md
│   ├── rag-layer.md
│   └── agent.md
│
├── attacks/                           the attack catalog
│   ├── ATTACK_INDEX.md
│   ├── rag/                           a0, a1a, a1b, a1c, a2, a7, a8, a10
│   ├── mcp/                           a4, a5, a11, a12 (a3, a6, a9 deferred)
│   ├── agent/                         (chunk #6)
│   ├── llm/                           (chunk #6)
│   └── chatbot/                       (chunk #6)
│
└── guides/                            how-to docs for the team
    ├── running-attacks.md
    ├── testbench.md
    └── adding-an-attack.md
```

---

## Where to start

- **First-time contributor**: read [architecture/overview.md](architecture/overview.md), then [setup.md](setup.md).
- **Running attacks**: [guides/running-attacks.md](guides/running-attacks.md).
- **Adding an attack**: [guides/adding-an-attack.md](guides/adding-an-attack.md), then the relevant subdirectory under [attacks/](attacks/).
- **Reviewing what exists vs. what is planned**: [attacks/ATTACK_INDEX.md](attacks/ATTACK_INDEX.md).

---

## Conventions

- Attack IDs are lowercase: `a1a`, `a4`, `a12` for the catalog inherited from the reference PDFs; `g*` / `l*` / `c*` for Agent, LLM, Chatbot surfaces.
- Five attack surfaces: **RAG**, **MCP/Tools**, **Agent**, **LLM**, **Chatbot**. Every attack belongs to exactly one.
- These docs are living. Update them as the code changes — replace stale content rather than deprecating in place.

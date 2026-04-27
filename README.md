# pharma_help

**Context Poisoning and Indirect Prompt Injection in Agentic AI: Measuring Vulnerabilities from Malicious External Data Sources.**

EC521 Cybersecurity, Boston University, Spring 2026.

---

## What this is

pharma_help has two halves:

- **PharmaHelp** — the **target system**. A pharmaceutical research assistant for a fictitious biotech (BioForge). Built on Chainlit + LangGraph + Gemma (`gemma3:270m`), with a single MCP tool layer that fronts both ChromaDB retrieval and the action tools.
- **PharmaAttack** — the **attack service**. Tries to manipulate PharmaHelp through every available surface: RAG content, MCP tools, agent reasoning, the LLM itself, the Chainlit UI.

We measure attack success rate, defense detection rate, latency overhead, and persistence. Then we layer defenses and re-measure.

---

## Documentation

All design and operational docs live under [docs/](docs/). Start there.

| Where to start | Doc |
|---|---|
| What the project is and how it fits together | [docs/architecture/overview.md](docs/architecture/overview.md) |
| What's in scope and what's out | [SCOPE.md](SCOPE.md) |
| First-time setup | [docs/setup.md](docs/setup.md) |
| Running attacks | [docs/guides/running-attacks.md](docs/guides/running-attacks.md) |
| Adding a new attack | [docs/guides/adding-an-attack.md](docs/guides/adding-an-attack.md) |
| Master attack catalog | [docs/attacks/ATTACK_INDEX.md](docs/attacks/ATTACK_INDEX.md) |
| Reference PDFs (idea source, not spec) | [docs/](docs/) |
| Project plan and chunks | [TODO.md](TODO.md) |

---

## Quick start

```bash
# Setup (full instructions: docs/setup.md)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
ollama pull embeddinggemma gemma3:270m
python -m pharma_help.ingestion.setup_kb

# Run the chatbot
chainlit run app.py
```

---

## Project status

The target system is partially built (Chainlit + ChromaDB seeded; MCP servers in flight; agent uses mocks). Attack streams have working RAG and MCP scaffolding. Agent / LLM / Chatbot attack surfaces are not yet started.

See [TODO.md](TODO.md) for the six-phase plan.

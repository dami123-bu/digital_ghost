# Digital Ghost

**Context Poisoning and Indirect Prompt Injection in Agentic AI: Measuring Vulnerabilities from Malicious Data Sources**

Academic security research project — EC521 Cybersecurity, Boston University, Spring 2026.

---

## Overview

Digital Ghost builds a pharmaceutical research assistant as a **target system**, then attacks it and measures defenses. The system lets a researcher ask plain-English questions about drug compounds and get back relevant scientific literature plus an AI-written summary — powered by a RAG pipeline backed by PubMed abstracts.

The goal is to empirically measure how context poisoning and indirect prompt injection degrade agentic AI systems, and evaluate the effectiveness of defenses.

---

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run
python main.py
```

Requires API keys for Anthropic or OpenAI set as environment variables (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY`).

---

## Attack Surface

# MCP
# The PDF upload pathway
# Context Poisoning

---

## Architecture for RAG

```
digital_ghost/
├── config.py
├── data/                   # ChromaDB storage, drug list
├── ingestion/              # PubMed client, PDF parser, embedder
├── rag/                    # Vector store interface, retriever
├── agents/                 # ingest_agent.py, query_agent.py
├── synthesis/              # LLM synthesis wrapper
├── web/                    # FastAPI app, templates
└── scripts/                # setup_kb.py (one-time seed)
```

**Stack:**
- Python 3.12
- LangChain (ReAct agent pattern)
- ChromaDB (local vector store)
- Anthropic Claude / OpenAI GPT-4o
- SQLite (mock LIMS)

---

## Key Metrics

| Metric | Description |
|--------|-------------|
| ASR (Attack Success Rate) | Percentage of successful manipulations |
| Detection Rate | False positives/negatives on defense systems |
| Latency Overhead | Performance cost of defenses |
| Persistence Duration | How long poisoned context affects future queries |

---

## Testing Methodology

1. Baseline measurement on clean system
2. Attack injection with malicious documents (50–100 test corpus)
3. Behavior analysis and monitoring
4. Persistence testing across sessions

---

## Claude Code Skills

The `.claude/skills/` directory contains project-specific instructions that guide Claude Code (the AI assistant) when working in this repo. If you're using Claude Code, it will automatically follow these rules — you don't need to do anything manually.

| Skill | What it does |
|-------------|--------------|
| `architecture` | Best practices for RAG, agentic AI, and MCP server design |
| `testing` | Guidelines for writing tests with pytest in this project |
| `attack-spec` | Template for defining new attack vectors in a structured way |
| `documentation` | Guidelines for writing module/component docs |
| `changes` | Appends a summary entry to `CHANGES.md` after modifications |

If you're not using Claude Code, you can read these files directly — they contain useful context about how the project is structured and what conventions to follow.

---

## Further Reading

- [RAG.md](RAG.md) — how the RAG pipeline and agents work
- [project_team.md](project_team.md) — project overview and design decisions

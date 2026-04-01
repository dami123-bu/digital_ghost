# Digital Ghost

**Context Poisoning and Indirect Prompt Injection in Agentic AI: Measuring Vulnerabilities from Malicious External Data Sources**

Academic security research project — EC521 Cybersecurity, Boston University, Spring 2026.

---

## Overview

Digital Ghost builds a pharmaceutical research assistant as a **target system**, then attacks it and measures defenses. The system lets a researcher ask plain-English questions about drug compounds and get back relevant scientific literature plus an AI-written summary — powered by a RAG pipeline backed by PubMed abstracts.

The goal is to empirically measure how context poisoning and indirect prompt injection degrade agentic AI systems, and evaluate the effectiveness of defenses.

---

## Setup

IMPORTANT: Follow the steps in [SETUP.md](SETUP.md) exactly the first time you clone this project.

Subsequently, make sure Ollama is running before executing any scripts.

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
| `architecture` | Best practices for Python RAG, MCP, and agentic AI application architecture — covers ingestion, retrieval trust boundaries, agent design, and module structure |
| `testing` | Guidelines for writing tests in the Digital Ghost project |
| `attack-spec` | Define a new attack vector for the Digital Ghost experiment |
| `documentation` | Write or update documentation for a module, function, or component |


If you're not using Claude Code, you can read these files directly — they contain useful context about how the project is structured and what conventions to follow.

---

## Read the following for more details

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design, data flow, agent trust model, attack surfaces
- [RAG.md](RAG.md) — how the RAG pipeline and agents work

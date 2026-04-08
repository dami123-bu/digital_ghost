# pharma_help

**Context Poisoning and Indirect Prompt Injection in Agentic AI: Measuring Vulnerabilities from Malicious
External Data Sources**

Academic security research project — EC521 Cybersecurity, Boston University, Spring 2026.

---

## Overview

This is for a project that examines security and defenses for an agentic system. We want to identify attack surfaces
and vectors - we will collect metrics. There will be a target application (PharmaHelp), as well as an 
attack service (PharmaAttack). PharmaAttack that will attempt to attack PharmaHelp.

A fictitious biotech company BioForge needs an application to help with managing research documents. The proposed
app PharmaHelp will allow users to browse internal documents as well as public databases (Pubmed). This repository will
be implemented as a RAG. The app allows - 
- User can upload research documents 
- User can make natural language queries
- The app will generate a synthesis summary document. The synthesis, along with supporting documents
will be made available to the user.

This project is about finding out how badly an agentic AI system can be manipulated through its own data sources. 
We attack it from three angles — the RAG pipeline, the agentic reasoning loops, and the MCP layer, and measure how far the damage goes.

##TBD : MCP/OpenClaw 

## Technology

### PharmaHelp
Implemented in Python 3.12. ChromaDB for the vector store. Ollama for LLM inference (`gemma3:270m`) and embeddings (`nomic-embed-text`). LangGraph for the agent (multi-turn memory via `MemorySaver`). Chainlit for the chat UI.
TBD: RAG retrieval node, MCP/OpenClaw

---

## Setup

IMPORTANT: Follow the steps in [SETUP.md](SETUP.md) exactly the first time you clone this project.

**Python 3.12 is required.** The app will not run on Python 3.13 or 3.14 due to async compatibility issues with Chainlit's dependencies.

Subsequently, make sure Ollama is running before executing any scripts.

---

## Testing Methodology

### Phases

1. Baseline measurement on clean system
2. Attack injection with malicious documents (50–100 test corpus)
3. Defense evaluation — apply defenses and re-run same corpus
4. Persistence testing across turns and sessions

### Metrics

| Metric | Description |
|---|---|
| **Attack Success Rate (ASR)** | How often malicious content in the RAG or uploaded documents successfully manipulates the LLM's output or behavior |
| **Detection Rate** | How accurately defenses identify poisoned documents — including false positive and false negative rates |
| **Latency Overhead** | The performance cost of running defenses (input sanitization, output monitoring, trust scoring) relative to a clean baseline |
| **Persistence Duration** | How long a poisoned context window continues to affect subsequent queries, across turns and across sessions |
| **Injection Scope** | Whether a successful injection is limited to a single response or escalates to tool calls, data writes, or downstream agent actions |
| **Retrieval Bias** | The degree to which adversarial documents displace benign documents in top-k retrieval results |

---

## Claude Code Skills

The `.claude/skills/` directory contains project-specific instructions that guide Claude Code (the AI assistant) when working in this repo. If you're using Claude Code, it will automatically follow these rules — you don't need to do anything manually.

| Skill | What it does |
|-------------|--------------|
| `architecture` | Best practices for Python RAG, MCP, and agentic AI application architecture — covers ingestion, retrieval, agent design, and module structure |
| `testing` | Guidelines for writing tests in the pharma_help project |
| `attack-spec` | Define a new attack vector for the pharma_help experiment |
| `documentation` | Write or update documentation for a module, function, or component |
| `review` | Review Python code for general quality — repeated code, overly long methods, naming, file placement, and LangChain/RAG patterns. Run with `/review` |


If you're not using Claude Code, you can read these files directly — they contain useful context about how the project is structured and what conventions to follow.

---

## Running the UI

Make sure Ollama is running, then:

```bash
chainlit run app.py
```

The UI will be available at `http://localhost:8000`.

---

## Read the following for more details

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design, data flow, agent trust model, attack surfaces
- [RAG.md](RAG.md) — how the RAG pipeline and agents work

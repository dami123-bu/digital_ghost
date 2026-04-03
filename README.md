# pharma_help

**Context Poisoning and Indirect Prompt Injection in Agentic AI: Measuring Vulnerabilities from Malicious External Data Sources**

Academic security research project — EC521 Cybersecurity, Boston University, Spring 2026.

---

## Overview

pharma_help is an app that helps scientists conduct drug discovery research. 
This is also our **target system**, we will attack it and measures defenses.

pharma_help is an app deployed at a pharmaceutical company. It has a RAG repository which contains publicly available research 
data, as well as research results from experiments conducted at the company itself. 

The interfaces provided are
- Employees can upload files with research results
- Employees can query the app for drug information 
- A synthesized summary with files are provided to the employee
- TBD MCP/Open Claw Layer

Employees can make plain-English questions about drug compounds. DG queries the RAG and, when relevant, fetches fresh 
abstracts from PubMed — which are then stored back into the RAG. Employees can also upload internal research documents as PDFs.

pharma_help generates an LLM-powered synthesis, and provides this to the user, along with relevant documents.

This project is about finding out how badly an agentic AI system can be manipulated through its own data sources. 
We attack it from three angles — the RAG pipeline, the agentic reasoning loops, and the MCP layer, and measure how far the damage goes.

---

## Setup

IMPORTANT: Follow the steps in [SETUP.md](SETUP.md) exactly the first time you clone this project.

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
| `architecture` | Best practices for Python RAG, MCP, and agentic AI application architecture — covers ingestion, retrieval trust boundaries, agent design, and module structure |
| `testing` | Guidelines for writing tests in the pharma_help project |
| `attack-spec` | Define a new attack vector for the pharma_help experiment |
| `documentation` | Write or update documentation for a module, function, or component |


If you're not using Claude Code, you can read these files directly — they contain useful context about how the project is structured and what conventions to follow.

---

## Read the following for more details

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design, data flow, agent trust model, attack surfaces
- [RAG.md](RAG.md) — how the RAG pipeline and agents work

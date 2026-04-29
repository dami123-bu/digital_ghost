# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pharma_help** is an academic security research project (EC521 Cybersecurity, BU Spring 2026) 
that measures and defends against context poisoning and indirect prompt injection attacks in 
agentic AI systems.

**Team**: Joshua Emmanuel, Damayanti Gupta, Chaudhry Wasam Ur Rehman, Julie Green, Xinyi Xie, Yiyang Hong

## Three Primary Attack Vectors

This project investigates three critical attack vectors:

1. **Indirect Prompt Injection via Malicious Documents**: Embedding malicious instructions in PDFs, 
   websites, or databases that manipulate the AI's behavior without the user's knowledge when 
   retrieved by an agentic system.

2. **Context Poisoning in RAG**: Poisoning vector databases or knowledge bases so that RAG systems 
   persistently return manipulated outputs across multiple user sessions.

3. **Tool Use Vulnerabilities via MCP**: Malicious tool descriptions or poisoned API responses that 
   hijack agent behavior and lead to unauthorized actions.

## Tech Stack

- **Language**: Python 3.12
- **Agent Framework**: LangChain (ReAct agent pattern)
- **Vector DB**: ChromaDB (local, no server)
- **LLM**: Ollama (`gemma3:270m` for synthesis, `embeddinggemma` for embeddings)
- **Database**: SQLite (mock LIMS system)

# CRITICAL
Do not run any git commands

# Startup
Read all the .md files, both in root directory, and in docs directory. 
Do not consider files in docs in the bak and my_eyes directories. Do not use DAMI_RULES.md unless asked to.

## Architecture
When proposing a plan or doing any architecture, first read `.claude/skills/architecture/SKILL.md`

## Key Metrics

- **ASR (Attack Success Rate)**: Goal hijacking, data exfiltration, unauthorized actions
- **Persistence**: Memory retention, cross-session contamination
- **Detection Evasion**: False positives/negatives on defense systems
- **Latency Overhead**: Performance impact of defenses (target: accuracy >95%)
- **Impact Severity**: CVSS-like scoring

## Testing
When writing or modifying any test files, first read `.claude/skills/testing/SKILL.md`

## Testing Methodology (4-Phase)

1. **Phase 1 — Baseline Measurement**: Test clean system performance
2. **Phase 2 — Attack Injection**: Introduce malicious documents (50-100 corpus: PDFs, web pages, JSON) 
   into data sources, ranging from simple to multi-stage attacks
3. **Phase 3 — Behavior Analysis**: Monitor and log agent decisions, tool calls, and outputs
4. **Phase 4 — Persistence Testing**: Evaluate long-term impact of poisoned context across sessions

**Benchmarks used for evaluation**: Agent Security Bench (ASB: 10 scenarios, 400+ tools), 
CVE-Bench (real-world vulnerabilities), OWASP Agentic AI Top 10 2026.

**Comparison targets**: Microsoft Prompt Shields, OpenAI hardening, PALADIN.

## Mitigation Strategies (to implement and evaluate)

1. **Input Sanitization**: Microsoft Prompt Shields (LLM classifier), custom NLP filters, structural validation
2. **Privilege Separation**: Dual-LLM architecture, capability-based security, human-in-the-loop for high-risk actions
3. **Output Monitoring**: Real-time behavioral analysis, provenance tracking, alert system
4. **Cryptographic Verification**: Content hashing (SHA-256), digital signatures, MCP server pinning
5. **Context Isolation**: Ephemeral contexts, namespace isolation per user/tenant, containerized execution

## Deliverables

1. Vulnerable system demo
2. Attack toolkit
3. Hardened system with all defenses integrated
4. Real-time evaluation dashboard

## Domain Context

This project uses a pharmaceutical research scenario (drug compounds, IC50 values, clinical labels). 
The knowledge base contains synthetic research documents. Attack vectors include hidden 
instructions in documents, RAG context poisoning, and tool-use manipulation via MCP.

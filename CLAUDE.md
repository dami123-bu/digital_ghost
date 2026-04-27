# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pharma_help** is an academic security research project (EC521 Cybersecurity, BU Spring 2026) 
that measures and defends against context poisoning and indirect prompt injection attacks in 
agentic AI systems.

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
When proposing a plan or doing any architecture,  first read `.claude/skills/architecture/SKILL.md`


## Key Metrics

- **ASR (Attack Success Rate)**: Percentage of successful manipulations
- **Detection Rate**: False positives/negatives on defense systems
- **Latency Overhead**: Performance impact of defenses
- **Persistence Duration**: How long poisoned context affects future queries

## Testing
When writing or modifying any test files, first read `.claude/skills/testing/SKILL.md`

## Testing Methodology specific to security
Testing follows a structured before/after comparison:
1. Baseline measurement on clean system
2. Attack injection with malicious documents (50-100 test corpus)
3. Behavior analysis and monitoring
4. Persistence testing across sessions

## Domain Context

This project uses a pharmaceutical research scenario (drug compounds, IC50 values, clinical labels). 
The knowledge base contains synthetic research documents. Attack vectors include hidden 
instructions in documents, RAG context poisoning, and tool-use manipulation.

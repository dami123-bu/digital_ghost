# Digital Ghost — Project Overview

## What We're Building

A web application that lets a researcher ask plain-English questions about pharmaceutical drugs and get back relevant scientific literature plus an AI-written summary. It serves as the **target system** for our security research — we build it, then attack it (context poisoning, prompt injection) and measure defenses.

## RAG and agents
### Background: What is a RAG application?

LLMs (like ChatGPT) are trained on general internet data and have a knowledge cutoff. They don't know about proprietary documents, recent papers, or domain-specific databases. **Retrieval-Augmented Generation (RAG)** solves this by giving the LLM a private search engine at query time:

1. **Offline:** Documents are split into chunks, converted to numerical vectors (embeddings) that capture semantic meaning, and stored in a vector database.
2. **At query time:** The user's question is converted to a vector. The database finds the chunks whose vectors are closest — i.e., most semantically similar — and hands those chunks to the LLM as context.
3. **The LLM answers** using those chunks as its source material, rather than guessing from training data.

This is why RAG systems are widely used in enterprise and research settings — and why they are an interesting attack surface. Whoever controls what goes into the knowledge base controls what the LLM "knows."

### What the App Does

- **Setup:** fetch the top 50 PubMed abstracts for each drug in our list and embed them into the knowledge base
- **Ingest:** user submits a drug name or uploads PDFs → added to the knowledge base
- **Query:** user asks a natural language question → app returns the 20 best-matching articles as a ZIP file and an LLM-written synthesis in a text box

---

## Core Components

### 1. Knowledge Base
A vector database (RAG) storing biomedical article chunks. Seeded via a one-time setup script (top 50 PubMed abstracts per drug). Users can also add documents at runtime.

**Decision needed:** Which vector DB? (ChromaDB, Qdrant, Weaviate, pgvector, ...)

### 2. Two LangChain Agents
All reads and writes to the knowledge base go through agents — nothing touches the store directly.

- **Ingest Agent** — given a drug name or PDF, fetches/parses text and adds it to the knowledge base
- **Query Agent** — given a natural language query, retrieves the top matching documents and produces an LLM synthesis

**Decision needed:** Agent pattern (ReAct, tool-calling, plan-and-execute, ...)?

### 3. LLM
Used for embeddings and for synthesis responses.

**Decision needed:** Which LLM and embedding model? (Ollama local, OpenAI, Anthropic, ...)

### 4. Web Interface
Single-page app with two panels: one for ingesting documents, one for querying.

**Decision needed:** Frontend approach (plain HTML/JS, React, Streamlit, Gradio, ...)?

---

## Module Sketch

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

---

## Open Decisions

| # | Question |
|---|----------|
| 1 | Vector DB choice |
| 2 | LLM and embedding model (local vs. API) |
| 3 | Agent reasoning pattern |
| 4 | Frontend framework |
| 5 | PubMed article depth (abstracts only vs. full-text via PMC) |
| 6 | LLM synthesis delivery (streaming vs. batch) |

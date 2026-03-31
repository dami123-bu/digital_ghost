# Digital Ghost — RAG Application Architecture

## Project Overview

This is an project for EC521 Cybersecurity (BU Spring 2026). It is a biomedical application with a RAG, Agents, and MCP(OpenClaw). It serves as the **target system** for security research: we build it, then measure and defend against context poisoning and  prompt injection attacks.

So far, the app allows users to query a biomedical knowledge base (PubMed articles) using natural language, upload their own PDFs into the knowledge base, and receive LLM-synthesized answers alongside the source documents. The setup and RAG part has been implemented. The rest are TBD once the agents are done.

TBD - agents, attack mechanisms, MCP(OpenClaw) 

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Language | Python 3.12 | |
| Vector DB | ChromaDB (local) | Zero-config, Python-native, LangChain integration, sufficient for ~2,500 docs |
| LLM (synthesis) | Ollama (`mistral:7b`) | Local, no data leaves machine — critical for security research |
| Embeddings | Ollama (`nomic-embed-text`) | Dedicated embedding model, better than using a generative model |
| Agent Framework | LangChain (ReAct pattern) | Agent design TBD |
| PDF parsing | pypdf | |
| PubMed API | NCBI E-utilities (httpx) | Free, rate-limited; abstracts are free-tier |

---

## File Layout

```
digital_ghost/
├── pyproject.toml
├── PROJECT.md                  # This file
├── config.py                   # Ollama URL, model names, ChromaDB path, PubMed settings
│
├── data/
│   └── chroma/                 # ChromaDB persistent storage
│
├── scripts/
│   ├── setup_kb.py             # One-time setup: drugs.txt → PubMed → ChromaDB
│   └── drugs.txt               # List of drug names (one per line)
│
├── src/digital_ghost/          # Application package (empty — __init__.py only)
│   ├── ingestion/              # planned: pubmed.py, pdf_parser.py, embedder.py
│   ├── rag/                    # planned: store.py, retriever.py
│   ├── agents/                 # TBD
│   └── synthesis/              # planned: synthesizer.py
│
├── main.py                     # Entry point (placeholder)
└── tests/
```

---

## Agents

Agent design (number, responsibilities, tool assignment) is TBD. LangChain ReAct agents will mediate all interactions with the knowledge base — no code outside agents writes to or reads from ChromaDB directly.

TBD Attack plan

---

## Data Flow

### Setup (run once via `scripts/setup_kb.py`)

```
drugs.txt
  → pubmed.py (E-utilities, top 50 abstracts per drug)
  → embedder.py (chunk → embed via nomic-embed-text → upsert ChromaDB)
```

### Ingest (planned)

```
scripts/ingest.py --drug <name> [--pdf <file>]
  → agent(s) (ReAct loop)
      → fetch_pubmed(drug_name)
      → parse_pdf(file_bytes)
      → ingest_document(text, meta)
  → ChromaDB
```

### Query (planned)

```
scripts/query.py --query "<natural language query>"
  → agent(s) (ReAct loop)
      → retrieve_docs(query, k=20)   → ChromaDB
      → synthesize(query, docs)      → Ollama LLM
  → stdout: ranked articles + synthesis text
```

---

## Setup Script

`scripts/setup_kb.py` is run once to seed the knowledge base. It:
1. Reads `scripts/drugs.txt` (one drug per line)
2. For each drug, fetches the top N PubMed abstracts via E-utilities
3. Upserts abstracts directly into ChromaDB (`data/chroma/`)

Expected corpus size: ~50 drugs × 50 abstracts = ~2,500 documents.

---


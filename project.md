# Digital Ghost — RAG Application Architecture

## Project Overview

A pharmaceutical research RAG application for EC521 Cybersecurity (BU Spring 2026). The application is the **target system** for security research: we build it, then measure and defend against context poisoning and indirect prompt injection attacks.

The app allows users to query a biomedical knowledge base (PubMed articles) using natural language, upload their own PDFs into the knowledge base, and receive LLM-synthesized answers alongside the source documents.

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Language | Python 3.12 | |
| Web Framework | FastAPI + Jinja2 | Minimal, no build step, easy to reason about |
| Vector DB | ChromaDB (local) | Zero-config, Python-native, LangChain integration, sufficient for ~2,500 docs |
| LLM (synthesis) | Ollama (`mistral:7b` or `llama3.2`) | Local, no data leaves machine — critical for security research |
| Embeddings | Ollama (`nomic-embed-text`) | Dedicated embedding model, better than using a generative model |
| Agent Framework | LangChain (ReAct pattern) | Two agents: ingest agent and query agent |
| PDF parsing | pypdf | |
| PubMed API | NCBI E-utilities (httpx) | Free, rate-limited; abstracts are free-tier |

---

## File Layout

```
digital_ghost/
├── pyproject.toml
├── project.md                  # This file
├── config.py                   # Ollama URL, model names, ChromaDB path, PubMed settings
│
├── data/
│   ├── chroma/                 # ChromaDB persistent storage
│   └── drugs.txt               # List of drug names (one per line)
│
├── ingestion/
│   ├── pubmed.py               # PubMed E-utilities client: fetch top-N abstracts per drug
│   ├── pdf_parser.py           # Extract text from uploaded PDFs (pypdf)
│   └── embedder.py             # Chunk text, embed via Ollama, upsert to ChromaDB
│
├── rag/
│   ├── store.py                # ChromaDB collection init and query interface
│   └── retriever.py            # LangChain retriever wrapping store.py (returns top-K docs)
│
├── agents/
│   ├── ingest_agent.py         # LangChain ReAct agent — tool: ingest_document(text, metadata)
│   └── query_agent.py          # LangChain ReAct agent — tool: retrieve_docs(query, k=20)
│
├── synthesis/
│   └── synthesizer.py          # query + retrieved docs → LLM synthesis via Ollama
│
├── web/
│   ├── app.py                  # FastAPI app: routes, lifespan startup
│   ├── templates/
│   │   └── index.html          # Single-page UI
│   └── static/
│       └── style.css
│
├── scripts/
│   └── setup_kb.py             # One-time setup: drugs.txt → PubMed → ChromaDB
│
└── tests/
```

---

## Agents

LangChain ReAct agents mediate all interactions with the knowledge base. No code outside the agents writes to or reads from ChromaDB directly.
An additional agent that attacks the system.

### Ingest Agent (`agents/ingest_agent.py`)

Responsible for adding documents to the knowledge base.

**Tools available:**
- `fetch_pubmed(drug_name, n=50)` → fetches top-N abstracts from PubMed E-utilities
- `parse_pdf(file_bytes)` → extracts text from a PDF
- `ingest_document(text, metadata)` → chunks, embeds, and upserts to ChromaDB

**Invoked by:** `POST /ingest` (user submits a drug name and/or PDF upload)

**Behavior:** The agent reasons over what was provided (drug name, PDF, or both) and calls the appropriate tools in sequence to get text into ChromaDB with correct metadata tags.

### Query Agent (`agents/query_agent.py`)

Responsible for retrieving relevant documents and producing a synthesized answer.

**Tools available:**
- `retrieve_docs(query, k=20)` → queries ChromaDB, returns top-K chunks with metadata and scores
- `synthesize(query, docs)` → passes query + docs to Ollama LLM, returns synthesis text

**Invoked by:** `POST /query` (user submits a natural language query)

**Behavior:** The agent retrieves the top 20 matching articles, then calls the synthesizer to produce a summary. Both the raw articles and the synthesis are returned to the web layer.

---

## Data Flow

### Setup (run once via `scripts/setup_kb.py`)

```
drugs.txt
  → pubmed.py (E-utilities, top 50 abstracts per drug)
  → embedder.py (chunk → embed via nomic-embed-text → upsert ChromaDB)
```

### Ingest (user-triggered via web)

```
Browser: drug name + optional PDF(s)
  → POST /ingest
  → ingest_agent.py (ReAct loop)
      → fetch_pubmed(drug_name)      [if drug name provided]
      → parse_pdf(file_bytes)        [if PDF provided]
      → ingest_document(text, meta)
  → ChromaDB
```

### Query (user-triggered via web)

```
Browser: natural language query
  → POST /query
  → query_agent.py (ReAct loop)
      → retrieve_docs(query, k=20)   → ChromaDB
      → synthesize(query, docs)      → Ollama LLM
  → Response: { articles: [...], synthesis: "..." }
  → UI: synthesis text box + article list + ZIP download
```

---

## UI (Single Page — `web/templates/index.html`)

Two panels side by side:

**Left — Ingest Panel**
- Text field: drug name
- File picker: upload one or more PDFs
- Button: "Add to Knowledge Base"
- Status message (success/error from ingest agent)

**Right — Query Panel**
- Text area: natural language query
- Button: "Search"
- Results section:
  - Synthesis text box (LLM output)
  - Ranked article list with: title, drug tag, PMID (if from PubMed), similarity score
  - "Download Results (ZIP)" button — ZIP contains ranked article text files, one per article

---

## Dependencies

```toml
fastapi
uvicorn
langchain
langchain-community
langchain-ollama
chromadb
pypdf
httpx
jinja2
python-multipart
```

---

## Setup Script

`scripts/setup_kb.py` is run once before the web app is started. It:
1. Reads `data/drugs.txt` (one drug per line)
2. For each drug, fetches the top 50 PubMed abstracts via E-utilities
3. Passes each abstract through the ingest pipeline (chunk → embed → ChromaDB)

Expected corpus size: ~50 drugs × 50 abstracts = ~2,500 documents.

---

## Open Questions

1. **Drug list** — needs to be provided before `setup_kb.py` can run.
2. **NCBI API key** — E-utilities is rate-limited to 3 req/s without a key, 10 req/s with. An API key is recommended for setup.
3. **Article depth** — PubMed abstracts are free-tier. Full-text requires PMC Open Access filtering. Default: abstracts only.
4. **Ollama model selection** — `mistral:7b` (better quality) vs `llama3.2:3b` (faster). TBD.
5. **Streaming** — LLM synthesis can stream to the UI via SSE or be returned as a complete response. TBD.

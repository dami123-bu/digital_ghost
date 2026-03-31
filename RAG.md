# Digital Ghost — RAG Application Architecture

This is the RAG component for Digital Ghost

The app allows users to query a biomedical knowledge base (PubMed abstracts) using natural language, upload their own PDFs into the knowledge base, and receive LLM-synthesized answers alongside the source documents.

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Language | Python 3.12 | |
| Vector DB | ChromaDB (local persistent) | Zero-config, Python-native, LangChain integration |
| LLM (synthesis) | Ollama / `mistral:7b` | Local — no data leaves machine, critical for security research |
| Embeddings | Ollama / `nomic-embed-text` | Dedicated embedding model |
| Agent Framework | LangChain (ReAct pattern) | Agent design TBD |
| PDF parsing | pypdf | Attack surface for malicious document injection |
| PubMed API | NCBI E-utilities (httpx) | Free-tier; abstracts only |

---

## File Layout

```
digital_ghost/
├── config.py                   # Ollama URLs, model names, ChromaDB path, PubMed settings
├── scripts/
│   ├── setup_kb.py             # One-time seed: drugs.txt → PubMed → ChromaDB
│   └── drugs.txt               # List of drug names (one per line)
├── data/
│   └── chroma/                 # ChromaDB persistent storage
└── src/digital_ghost/          # Source package (planned)
    ├── ingestion/
    │   ├── pubmed.py            # PubMed E-utilities client
    │   ├── pdf_parser.py        # Extract text from PDFs (pypdf)
    │   └── embedder.py          # Chunk text, embed via Ollama, upsert to ChromaDB
    ├── rag/
    │   ├── store.py             # ChromaDB collection init and query interface
    │   └── retriever.py         # LangChain retriever (returns top-K docs)
    ├── agents/                  # Agent design TBD
    ├── synthesis/
    │   └── synthesizer.py       # query + retrieved docs → LLM synthesis via Ollama
    └── web/
        ├── app.py               # FastAPI application
        └── templates/index.html
```

---

## Agents

LangChain ReAct agents mediate all interactions with the knowledge base. No code outside the agents writes to or reads from ChromaDB directly.

Two agents mediate all interactions: an **ingest agent** (tools: `fetch_pubmed`, `parse_pdf`, `ingest_document`) and a **query agent** (tools: `retrieve_docs`, `synthesize`). Key design constraint: retrieved content must be sanitized before being passed to any agent that can take actions — this is the trust boundary that limits indirect prompt injection.

---

## Data Flow

### Setup (run once)

```
scripts/drugs.txt
  → pubmed.py (E-utilities, top-N abstracts per drug)
  → embedder.py (chunk → embed via nomic-embed-text → upsert ChromaDB)
```

`scripts/setup_kb.py` implements this directly. It reads `scripts/drugs.txt`, fetches abstracts from PubMed, embeds them via `nomic-embed-text` through Ollama, and upserts into the `pubmed` collection in ChromaDB. Idempotent — skips if collection already populated.

### Ingest (planned)

```
scripts/ingest.py --drug <name> [--pdf <file>]
  → agent(s) (ReAct loop)
      → fetch_pubmed(drug_name)
      → parse_pdf(file_bytes)
      → ingest_document(text, metadata)
  → ChromaDB
```

### Query (planned)

```
scripts/query.py --query "<natural language query>"
  → agent(s) (ReAct loop)
      → retrieve_docs(query, k=20)  → ChromaDB (similarity threshold >= 0.5)
      → sanitize chunks             ← trust boundary
      → synthesize(query, docs)     → Ollama mistral:7b
  → stdout: ranked articles + synthesis text
```

# Architecture

pharma_help builds a pharmaceutical research assistant as a **target system**, attacks it, and measures defenses. The system lets a researcher ask questions about drug compounds and get back relevant PubMed literature plus an AI-generated summary — powered by a RAG pipeline.

---

## Technology Stack

| Layer                  | Technology                  |
|------------------------|-----------------------------|
| Language               | Python 3.12                 |
| Agent framework        | LangChain                   |
| Vector store           | ChromaDB (local persistent) |
| LLM                    | Ollama / `mistral:7b`       |
| Embeddings             | Ollama / `nomic-embed-text` |
| Web interface          | TBD                         |
| OpenClaw               | TBD                         |
| Attack Agent Framework | LangChain                   |


---

## Directory structure

First cut, exact details TBD

```
pharma_help/
├── config.py                   # Ollama URLs, model names, ChromaDB path, PubMed settings
├── scripts/
│   ├── setup_kb.py             # One-time seed: drugs.txt → PubMed → ChromaDB
│   └── drugs.txt               # List of drug names (one per line)
├── data/
│   └── chroma/                 # ChromaDB persistent storage
└── src/pharma_help/          # Source package (planned)
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

TBD OpenClaw


---


## Components

**Database Seeding(offline)**

```
drugs.txt → PubMed (NCBI) → parse abstracts → embed (nomic-embed-text) → ChromaDB
```

**Query (online)**

```
User question → embed → ChromaDB similarity search → mistral:7b → response
```

...

---

## Agent design (LangChain, LangGraph)

Agents mediate all interactions with the knowledge base. Multi-turn needed.
TBD how many agents and exact functionality
suggested tools: 
- `fetch_pubmed`, `parse_pdf`, `ingest_document` , `retrieve_docs`, `synthesize`

---

## OpenClaw

TBD

---

## Attack Surfaces

Malicious PDF upload 
RAG context poisoning
Agents
....

---

## Attack Mechanism

Could include agents that attack the surfaces. Self- teaching - they learn better mechanisms with time.

---



## Configuration

All values live in `config.py`, overridable via environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_LLM_MODEL` | `mistral:7b` | LLM for synthesis |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `CHROMA_COLLECTION_PUBMED` | `pubmed` | ChromaDB collection for PubMed abstracts |
| `RETRIEVER_TOP_K` | `20` | Candidates per query |
| `SIMILARITY_THRESHOLD` | `0.5` | Minimum cosine similarity |
| `PUBMED_MAX_RESULTS` | `50` | Max articles per drug |
| `NCBI_API_KEY` | `None` | Optional; raises rate limit to 10 req/s |

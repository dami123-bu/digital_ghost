# Architecture

Digital Ghost builds a pharmaceutical research assistant as a **target system**, attacks it, and measures defenses. The system lets a researcher ask questions about drug compounds and get back relevant PubMed literature plus an AI-generated summary — powered by a RAG pipeline.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Agent framework | LangChain (ReAct) |
| Vector store | ChromaDB (local persistent) |
| LLM | Ollama / `mistral:7b` |
| Embeddings | Ollama / `nomic-embed-text` |
| Web interface | FastAPI (planned) |
| Mock LIMS | SQLite (planned) |

---

## How it works

**Ingestion (offline)**

```
drugs.txt → PubMed (NCBI) → parse abstracts → embed (nomic-embed-text) → ChromaDB
```

**Query (online)**

```
User question → embed → ChromaDB similarity search → sanitize → mistral:7b → response
```

The sanitization step is the critical trust boundary — retrieved text is treated as untrusted input, never passed raw to the LLM.

---

## Agent design

Two agents mediate all interactions with the knowledge base:

- **Ingest agent** (`src/digital_ghost/agents/ingest_agent.py`) — tools: `fetch_pubmed`, `parse_pdf`, `ingest_document`
- **Query agent** (`src/digital_ghost/agents/query_agent.py`) — tools: `retrieve_docs`, `synthesize`

Key constraint: retrieved content must be sanitized before being passed to any agent that can take actions. This is the trust boundary that limits indirect prompt injection — raw document text should never reach a tool-calling agent directly.

---

## Directory structure

```
digital_ghost/
├── config.py               # All configuration (env vars + constants)
├── data/chroma/            # ChromaDB persistent store
├── scripts/
│   ├── setup_kb.py         # Seeds ChromaDB from PubMed (working)
│   └── drugs.txt           # 10 test compounds
└── src/digital_ghost/      # Source package (planned)
    ├── ingestion/          # pubmed.py, pdf_parser.py, embedder.py
    ├── rag/                # store.py, retriever.py
    ├── agents/             # TBD
    ├── synthesis/          # synthesizer.py
    └── web/                # FastAPI app + templates
```

Only `config.py` and `scripts/setup_kb.py` contain working code. Everything under `src/` is planned.

---

## Security research layer

The project deliberately exposes attack surfaces for measurement.

**Attack surfaces**

| Vector | Entry point | Effect |
|--------|------------|--------|
| Malicious PDF upload | `parse_pdf` tool | Adversarial text injected into ChromaDB |
| RAG context poisoning | Poisoned embeddings | LLM output manipulated for all future queries |
| Tool-use manipulation | Document content | Agent tool calls hijacked via hidden instructions |

**Defenses measured**

- Sanitization at the retrieval → LLM boundary
- Agent privilege separation (ingest vs query)
- Similarity threshold (reject low-confidence chunks)
- Logging retrieved and discarded chunks

**Metrics**

| Metric | Definition |
|--------|-----------|
| ASR | Attack Success Rate — % of successful manipulations |
| Detection Rate | False positive / negative rate on defenses |
| Latency Overhead | Performance cost of defenses |
| Persistence Duration | How long poisoned context affects future queries |

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

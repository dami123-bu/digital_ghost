# Architecture

This project consists of two services: **PharmaHelp** (target) and **BioBreak** (attacker).

**PharmaHelp** is a pharmaceutical research assistant for the fictitious company BioForge. It lets researchers ask questions about drug compounds and get back relevant PubMed literature plus an AI-generated summary — powered by a RAG pipeline.

**BioBreak** is the attack service. It attempts to manipulate PharmaHelp through its data sources — poisoning the RAG, exploiting agent reasoning loops, and abusing the MCP layer. Metrics are collected to measure attack success and defense effectiveness.

---

## Technology Stack

| Layer                  | Technology                  |
|------------------------|-----------------------------|
| Language               | Python 3.12                 |
| Agent framework        | LangChain / LangGraph       |
| Vector store           | ChromaDB (local persistent) |
| LLM                    | Ollama / `gemma3:270m`         |
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
User question → embed → ChromaDB similarity search → gemma3:270m → response
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

## BioBreak (Attack Service)

BioBreak is the adversarial counterpart to PharmaHelp. It targets PharmaHelp's attack surfaces by injecting malicious content into the RAG, crafting adversarial documents, and probing agent behavior.

Attack angles:
- **RAG poisoning** — inject malicious documents into ChromaDB to bias retrieval
- **Agentic loop manipulation** — craft inputs that hijack LangChain/LangGraph agent reasoning
- **MCP layer abuse** — exploit tool-use interfaces (TBD)

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
| `OLLAMA_LLM_MODEL` | `gemma3:270m` | LLM for synthesis |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `CHROMA_COLLECTION_PUBMED` | `pubmed` | ChromaDB collection for PubMed abstracts |
| `RETRIEVER_TOP_K` | `20` | Candidates per query |
| `SIMILARITY_THRESHOLD` | `0.5` | Minimum cosine similarity |
| `PUBMED_MAX_RESULTS` | `50` | Max articles per drug |
| `NCBI_API_KEY` | `None` | Optional; raises rate limit to 10 req/s |

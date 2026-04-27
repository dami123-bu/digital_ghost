# RAG layer

## Role

The RAG layer is what lets the agent answer questions grounded in real documents instead of hallucinating. It is also the **primary attack surface** of the entire system — every poisoned document the attacker plants flows through here.

In MCP terms, the RAG layer is **Server 2 — Knowledge Base** ([mcp-layer.md](mcp-layer.md)). The agent never reads ChromaDB directly; it goes through that server's tools.

---

## Two collections

| Collection | Source | Trust |
|---|---|---|
| `pubmed` | Seeded by `pharma_help.ingestion.setup_kb` from NCBI E-utilities. PubMed abstracts for the drugs in `data/drugs.txt`. | Trusted external. **Not** an attack target — the project does not poison PubMed. |
| `internal_docs` | User-uploaded PDFs via the Chainlit UI. | **Untrusted**. Primary RAG attack surface. |

The split is intentional: `pubmed` provides a stable baseline, `internal_docs` is where attackers plant payloads.

For the attack lab, `pharma_attack/chroma_lab.py` clones benign records from `pubmed` into `pubmed_attack_lab` and injects payloads there — the source `pubmed` collection is never mutated.

---

## Storage

ChromaDB persistent on disk at `data/chroma/`. Embeddings via Ollama `nomic-embed-text`. Chunking: 512-token windows, 64-token overlap (configurable).

Tunables live in [src/pharma_help/config.py](../../src/pharma_help/config.py). All paths are env-var driven; defaults are relative to the project root (the cwd from which Chainlit and the ingestion module are launched).

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `CHROMA_COLLECTION_PUBMED` | `pubmed` | Collection name |
| `RETRIEVER_TOP_K` | `20` | Top-K candidates per query |
| `SIMILARITY_THRESHOLD` | `0.5` | Minimum cosine similarity |
| `PHARMA_DATA_DIR` | `data` | Root of on-disk data; `CHROMA_DIR` and `DRUGS_FILE` derive from it |
| `CHROMA_DIR` | `data/chroma` | ChromaDB persistent client path |
| `DRUGS_FILE` | `data/drugs.txt` | Drug list seeded into the `pubmed` collection |

---

## KB server tools (canonical)

Per [Server Schematics PDF](../PharmaHelp%20MCP%20Server%20Schematics.pdf) p.5.

| Tool | Privilege | Notes |
|---|---|---|
| `query_knowledge_base(query, collection, top_k, similarity_threshold)` | Read-only | The retrieval entrypoint. Returns top-K chunks with metadata and scores. |
| `upsert_document(collection, document_id, text, metadata)` | **Write** | The ingestion entrypoint. Used legitimately by the Doc Processor flow; abused by **a7** (persistence) and **a1** (active poisoning). |
| `delete_document(collection, document_id)` | **Destructive** | Targeted-deletion attack vector for **a7**. |
| `list_documents(collection)` | Read-only | Reconnaissance value — reveals the full document inventory. |

Resources: `kb://collections`, `kb://stats`. Both leak inventory and statistics — useful to attackers.

---

## Data flow

### Setup (one-time)

```
data/drugs.txt
    → python -m pharma_help.ingestion.setup_kb
    → NCBI E-utilities (httpx)
    → embed via nomic-embed-text
    → upsert to data/chroma/ pubmed collection
```

Idempotent: skips if collection already populated.

### Query (online — under construction)

```
User question (Chainlit)
    → LangGraph agent (Gemma)
    → query_knowledge_base tool
    → ChromaDB similarity search (top-K, threshold)
    → returns chunks with metadata
    → agent synthesizes answer
    → response with citations
```

**Current gap**: the agent's [tools.py](../../src/pharma_help/agents/tools.py) returns hardcoded mock documents instead of querying ChromaDB. Replacing that mock with a real query is part of TODO Phase 3.

### Ingest (online — under construction)

```
PDF upload (Chainlit)
    → validate_document (Doc Processor)
    → parse_pdf (Doc Processor)
    → chunk_text (Doc Processor)
    → upsert_document (KB server) → internal_docs collection
```

This entire flow is the [a2 PDF Trojan](../attacks/rag/a2-pdf-trojan.md) attack target.

---

## Why RAG is the primary attack surface

Per [Attack Schematics PDF](../PharmaHelp%20MCP%20Attack%20Schematics.pdf) and existing pharma_attack work:

1. **Persistence**. ChromaDB is on disk. Once a poisoned document is in, it survives session resets, app restarts, and even agent upgrades — until explicitly removed.
2. **Trust laundering**. Once content is in `internal_docs`, the agent treats it as authoritative internal source material. It does not know which chunks came from a malicious upload.
3. **Retrieval bias**. A document engineered to have high cosine similarity to common queries displaces legitimate results, even without containing instructions.
4. **Embedding survival**. Hidden text in PDFs (white-on-white, metadata, table cells) survives parsing and ends up embedded as if it were normal content.

RAG attacks are catalogued in [docs/attacks/rag/](../attacks/rag/): **a1a** passive, **a1b** active instruction, **a1c** volume, **a2** PDF trojan, **a7** persistence, **a8** context overflow, **a10** semantic obfuscation.

---

## Related

- [mcp-layer.md](mcp-layer.md) — KB server is one of the five MCP servers
- [agent.md](agent.md) — how the agent uses retrieved chunks
- [attacks/rag/](../attacks/rag/) — RAG-targeted attacks
- [guides/testbench.md](../guides/testbench.md) — running RAG attacks

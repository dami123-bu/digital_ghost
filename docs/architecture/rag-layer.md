# RAG layer

## Role

The RAG layer is what lets the agent answer questions grounded in real documents instead of hallucinating. It is also the **primary attack surface** of the entire system — every poisoned document the attacker plants flows through here.

The agent never reads ChromaDB directly. Retrieval is exposed as the `query_knowledge_base` tool on `main_server` ([mcp-layer.md](mcp-layer.md)). RAG goes through MCP like every other tool — uniform tool layer, uniform attack surface (description poisoning, response injection apply to retrieval the same way they apply to file/LIMS tools).

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

ChromaDB persistent on disk at `data/chroma/`. Embeddings via Ollama `embeddinggemma`. Chunking: 512-token windows, 64-token overlap (configurable).

Tunables live in [src/pharma_help/config.py](../../src/pharma_help/config.py). All paths are env-var driven; defaults resolve relative to the project root (the directory containing `pyproject.toml`, found by searching upward from `config.py`). cwd-independent.

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_EMBED_MODEL` | `embeddinggemma` | Embedding model |
| `CHROMA_COLLECTION_PUBMED` | `pubmed` | Collection name |
| `RETRIEVER_TOP_K` | `20` | Top-K candidates per query |
| `SIMILARITY_THRESHOLD` | `0.5` | Minimum cosine similarity |
| `PHARMA_DATA_DIR` | `data` | Root of on-disk data; `CHROMA_DIR` and `DRUGS_FILE` derive from it |
| `CHROMA_DIR` | `data/chroma` | ChromaDB persistent client path |
| `DRUGS_FILE` | `data/drugs.txt` | Drug list seeded into the `pubmed` collection |

---

## KB tool (built)

Lives on `main_server` ([src/pharma_help/mcp/servers/main_server.py](../../src/pharma_help/mcp/servers/main_server.py)) alongside the action tools.

| Tool | Privilege | Notes |
|---|---|---|
| `query_knowledge_base(query, k)` | Read-only | The retrieval entrypoint. Wraps `retrieve_docs`. Returns top-K chunks with metadata and scores. Attack target for **a1** (description poisoning, response injection on the chunks) and **a10** (semantic obfuscation). |

### Canonical tools — not built

The reference [Server Schematics PDF](../PharmaHelp%20MCP%20Server%20Schematics.pdf) p.5 also defines `upsert_document`, `delete_document`, and `list_documents` plus `kb://collections` / `kb://stats` resources. We don't expose those as MCP tools — ingest is a Chainlit upload handler, not a callable tool, and there's no listing/deletion surface. **a7** (persistence) targets ChromaDB directly through the ingest path, not through MCP.

---

## Data flow

### Setup (one-time)

```
data/drugs.txt
    → python -m pharma_help.ingestion.setup_kb
    → NCBI E-utilities (httpx)
    → embed via embeddinggemma
    → upsert to data/chroma/ pubmed collection
```

Idempotent: skips if collection already populated.

### Query (online — under construction)

```
User question (Chainlit)
    → LangGraph agent (Gemma)
    → MCP client → main_server → query_knowledge_base tool
    → retrieve_docs → ChromaDB similarity search (top-K, threshold)
    → returns chunks with metadata
    → agent synthesizes answer
    → response with citations
```

**Current gap**: real `retrieve_docs` exists in [src/pharma_help/agents/retrieval.py](../../src/pharma_help/agents/retrieval.py), but the agent's LangGraph node calls Gemma directly without invoking any tool, and there's no MCP client wired into the agent yet. Both are part of [PROJECT_PLAN.md](../../PROJECT_PLAN.md) chunks #1, #2, and #2b.

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

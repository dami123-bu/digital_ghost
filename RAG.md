# Digital Ghost — RAG Application Architecture

This is the RAG component for Digital Ghost

The app allows users to query a biomedical knowledge base (PubMed abstracts) using natural language, upload their own PDFs into the knowledge base, and receive LLM-synthesized answers alongside the source documents.

---


## Agents

LangChain ReAct agents mediate all interactions with the knowledge base. No code outside the agents writes to or reads from   
ChromaDB directly.

See - [ARCHITECTURE.md](ARCHITECTURE.md) for more details on agents.

---

## Data Flow



`scripts/setup_kb.py` implements this directly. It reads `scripts/drugs.txt`, fetches abstracts from PubMed, embeds them via `nomic-embed-text` through Ollama, and upserts into the `pubmed` collection in ChromaDB. Idempotent — skips if collection already populated.

### Ingest ()
TBD exact steps
```
scripts/ingest.py --drug <name> [--pdf <file>]
  → agent(s) (ReAct loop)
      → fetch_pubmed(drug_name)
      → parse_pdf(file_bytes)
      → ingest_document(text, metadata)
  → ChromaDB
```

### Query 
TBD exact steps

```
scripts/query.py --query "<natural language query>"
  → agent(s) (ReAct loop)
      → retrieve_docs(query, k=20)  → ChromaDB (similarity threshold >= 0.5)
      → sanitize chunks             ← trust boundary
      → synthesize(query, docs)     → Ollama mistral:7b
  → stdout: ranked articles + synthesis text
```

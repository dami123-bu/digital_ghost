# pharma_help — RAG Application Architecture

This is the RAG component for pharma_help.

The app allows users to query a biomedical knowledge base using natural language, 
upload their own PDFs into the knowledge base, and receive LLM-synthesized answers alongside the source documents.

The RAG contains two types of data:
- **PubMed abstracts** — fetched live from PubMed as queries are made, and stored into ChromaDB for future retrieval. PubMed is treated as a trusted, read-only external source and is not an attack target.
- **Internal company documents** — uploaded by employees as PDFs. This is the primary attack surface.

---


## Agents

LangChain ReAct agents mediate all interactions with the knowledge base. No code outside the agents writes to or reads from   
ChromaDB directly.

See - [ARCHITECTURE.md](ARCHITECTURE.md) for more details on agents.

---

## Data Flow


`scripts/setup_kb.py` is the seeding script. It reads `scripts/drugs.txt`, fetches abstracts from PubMed, 
mbeds them via `nomic-embed-text` through Ollama, and upserts into the `pubmed` collection in ChromaDB. 
Idempotent — skips if collection already populated.

### Ingest ()
TBD 


### Query 
TBD 



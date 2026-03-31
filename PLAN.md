# Digital Ghost — Project Plan

## Status

**Phase: Infrastructure complete. Application code not yet started.**

---

## What's Done

### Project scaffold
- `pyproject.toml` with all dependencies (`langchain`, `langchain-community`, `langchain-ollama`, `chromadb`, `pypdf`, `httpx`, `numpy`)
- `config.py` — central config for all env vars and path constants (Ollama URL/models, ChromaDB path, PubMed settings, retriever tuning)
- `src/digital_ghost/` — package skeleton (empty, placeholder files only)
- `scripts/drugs.txt` — 10 test drug compounds for KB seeding
- `SETUP.md` — complete onboarding guide (Python env, env vars, Ollama, KB seed)
- `ARCHITECTURE.md` — architecture decisions and security research design

### Knowledge base seeding
- `scripts/setup_kb.py` — working one-time script: reads `drugs.txt` → fetches PubMed abstracts via NCBI E-utilities → upserts into ChromaDB `pubmed` collection
- ChromaDB persists to `data/chroma/`

---

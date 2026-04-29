"""
rag/store.py

ChromaDB wrapper for the Digital Ghost RAG pipeline.

Two collections:
  pharma_clean    — clean PubMed + synthetic pharma docs (baseline)
  pharma_poisoned — same docs + 2 synthetic docs with hidden injection payloads

Public API:
  get_collection(mode)          → chromadb.Collection
  query_docs(query, mode, k)    → list[dict]  each has keys: id, text, metadata, distance
  format_docs(docs)             → str   ready to paste into a prompt
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

from config import (
    CHROMA_DIR,
    CHROMA_COLLECTION_CLEAN,
    CHROMA_COLLECTION_POISONED,
    CHROMA_COLLECTION_UPLOADS_CLEAN,
    CHROMA_COLLECTION_UPLOADS_POISONED,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
    RETRIEVER_TOP_K,
)

_COLLECTION_MAP = {
    "clean":        CHROMA_COLLECTION_CLEAN,
    "poisoned":     CHROMA_COLLECTION_POISONED,
    "defended":     CHROMA_COLLECTION_POISONED,  # defended uses poisoned data, strips injections
    "mcp_poisoned": CHROMA_COLLECTION_CLEAN,     # clean RAG for Vector 3 isolation
}

_UPLOADS_MAP = {
    "clean":        CHROMA_COLLECTION_UPLOADS_CLEAN,
    "poisoned":     CHROMA_COLLECTION_UPLOADS_POISONED,
    "defended":     CHROMA_COLLECTION_UPLOADS_POISONED,
    "mcp_poisoned": CHROMA_COLLECTION_UPLOADS_CLEAN,   # clean uploads too
}


def _embed_fn() -> OllamaEmbeddingFunction:
    return OllamaEmbeddingFunction(
        url=f"{OLLAMA_BASE_URL}/api/embeddings",
        model_name=OLLAMA_EMBED_MODEL,
    )


def _client() -> chromadb.PersistentClient:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection(mode: str) -> chromadb.Collection:
    """Return the ChromaDB collection for the given attack mode."""
    name = _COLLECTION_MAP.get(mode, CHROMA_COLLECTION_CLEAN)
    return _client().get_or_create_collection(
        name=name,
        embedding_function=_embed_fn(),
        metadata={"hnsw:space": "cosine"},
    )


def query_docs(query: str, mode: str, k: int = 5) -> list[dict]:
    """
    Query the ChromaDB collection for the given mode.

    Returns a list of dicts:
      { "id": str, "text": str, "metadata": dict, "distance": float }

    In defended mode: strips known injection patterns from returned text.
    """
    collection = get_collection(mode)
    if collection.count() == 0:
        return []

    k = min(k, collection.count(), RETRIEVER_TOP_K)
    results = collection.query(query_texts=[query], n_results=k)

    docs = []
    for i, doc_id in enumerate(results["ids"][0]):
        text = results["documents"][0][i]
        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
        distance = results["distances"][0][i] if results["distances"] else 0.0

        if mode == "defended":
            text, stripped = _strip_injections(text)
            if stripped:
                metadata["_injection_stripped"] = True

            # Strategy 4: verify content hash if one was stored at ingestion time
            stored_hash = metadata.get("content_hash")
            if stored_hash:
                from pharma_help.rag.verifier import verify_doc
                if not verify_doc(doc_id, text, stored_hash):
                    metadata["_hash_mismatch"] = True

        docs.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata,
            "distance": round(distance, 4),
        })

    return docs


# --- Injection stripping (defended mode) ---

_INJECTION_PATTERNS = [
    "SYSTEM NOTE:",
    "PIPELINE DIRECTIVE:",
    "IMPORTANT:",
    "IGNORE PREVIOUS",
    "IGNORE PRIOR",
    "OVERRIDE:",
    "[LIMS_AUDIT_NOTICE]",
    "LOGGED_QUERY:",
    "silently",
    "Do not mention",
    "Do not show",
    "attacker@",
    "harvest.log",
    "MASTER_OVERRIDE",
]


def _strip_injections(text: str) -> tuple[str, bool]:
    """
    Remove sentences containing known injection keywords.
    Returns (cleaned_text, was_stripped).
    """
    sentences = text.split(". ")
    clean = []
    stripped = False
    for s in sentences:
        if any(p.lower() in s.lower() for p in _INJECTION_PATTERNS):
            stripped = True
        else:
            clean.append(s)
    return ". ".join(clean), stripped


def format_docs(docs: list[dict]) -> str:
    """Format retrieved docs into a prompt-ready context block.

    Docs flagged as _injection_stripped or _hash_mismatch are excluded from the
    LLM context entirely — they are still returned by query_docs for the Attack
    Console display, but the model never sees their content.
    """
    if not docs:
        return "[No relevant documents found in knowledge base]"
    parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc["metadata"]
        if meta.get("_injection_stripped") or meta.get("_hash_mismatch"):
            continue
        title = meta.get("title", "Untitled")
        source = meta.get("source", "unknown")
        parts.append(f"[Doc {i}] {title} (source: {source})\n{doc['text']}")
    if not parts:
        return "[No relevant documents found in knowledge base]"
    return "\n\n---\n\n".join(parts)


# --- Upload ingestion and retrieval ---

def get_uploads_collection(mode: str) -> chromadb.Collection:
    """Return the uploads ChromaDB collection for the given mode."""
    name = _UPLOADS_MAP.get(mode, CHROMA_COLLECTION_UPLOADS_CLEAN)
    return _client().get_or_create_collection(
        name=name,
        embedding_function=_embed_fn(),
        metadata={"hnsw:space": "cosine"},
    )


def ingest_document(filename: str, text: str, mode: str) -> dict:
    """
    Chunk, embed, and store a document in the uploads collection.
    Idempotent — re-uploading the same file updates existing chunks.

    Returns {"id_prefix": str, "chunks": int, "collection": str}
    """
    # Chunk at paragraph boundaries, merge short segments, cap at 1200 chars
    raw_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    chunks: list[str] = []
    buf = ""
    for c in raw_chunks:
        if len(buf) + len(c) < 1200:
            buf = (buf + "\n\n" + c).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = c
    if buf:
        chunks.append(buf)
    if not chunks:
        chunks = [text]

    base = hashlib.sha256((filename + text[:100]).encode()).hexdigest()[:12]
    col = get_uploads_collection(mode)
    col.upsert(
        ids=[f"{base}-chunk-{n}" for n in range(len(chunks))],
        documents=chunks,
        metadatas=[{
            "source": "upload",
            "filename": filename,
            "title": filename,
            "content_hash": hashlib.sha256(c.encode()).hexdigest(),
            "upload_mode": mode,
            "chunk_index": n,
        } for n, c in enumerate(chunks)],
    )
    return {"id_prefix": base, "chunks": len(chunks), "collection": _UPLOADS_MAP[mode]}


def chunk_document_ephemeral(filename: str, text: str) -> list[dict]:
    """
    Chunk a document in memory only — never stored in ChromaDB.

    Returns the same shape as query_docs(): list of {id, text, metadata, distance}.
    distance is set to 0.0 so ephemeral chunks sort to the top when merged with
    KB results (direct-attach documents get highest retrieval priority).

    Use this for the /query/with-doc endpoint where the researcher attaches a file
    to a single query without wanting it persisted to the shared knowledge base.
    """
    raw_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    chunks: list[str] = []
    buf = ""
    for c in raw_chunks:
        if len(buf) + len(c) < 1200:
            buf = (buf + "\n\n" + c).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = c
    if buf:
        chunks.append(buf)
    if not chunks:
        chunks = [text]

    base = hashlib.sha256((filename + text[:100]).encode()).hexdigest()[:12]
    return [
        {
            "id": f"ephemeral-{base}-chunk-{n}",
            "text": chunk,
            "metadata": {
                "source": "ephemeral_upload",
                "filename": filename,
                "title": filename,
                "chunk_index": n,
            },
            "distance": 0.0,
        }
        for n, chunk in enumerate(chunks)
    ]


def query_uploads(query: str, mode: str, k: int = 3) -> list[dict]:
    """
    Query the uploads collection for the given mode.
    Returns same shape as query_docs(): list of {id, text, metadata, distance}.
    In defended mode: strips injection patterns and verifies content hashes.
    """
    collection = get_uploads_collection(mode)
    if collection.count() == 0:
        return []

    k = min(k, collection.count(), RETRIEVER_TOP_K)
    results = collection.query(query_texts=[query], n_results=k)

    docs = []
    for i, doc_id in enumerate(results["ids"][0]):
        text = results["documents"][0][i]
        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
        distance = results["distances"][0][i] if results["distances"] else 0.0

        if mode == "defended":
            text, stripped = _strip_injections(text)
            if stripped:
                metadata["_injection_stripped"] = True

            stored_hash = metadata.get("content_hash")
            if stored_hash:
                from pharma_help.rag.verifier import verify_doc
                if not verify_doc(doc_id, text, stored_hash):
                    metadata["_hash_mismatch"] = True

        docs.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata,
            "distance": round(distance, 4),
        })

    return docs

"""
Real ChromaDB retrieval against the populated `pubmed` collection.

The Chroma client and collection are built lazily on first call and cached
for the process lifetime.
"""

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

from pharma_help import config
from pharma_help.agents.retrieved_doc import RetrievedDoc

_collection: Collection | None = None


def _get_collection() -> Collection:
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    embed_fn = OllamaEmbeddingFunction(
        url=f"{config.OLLAMA_BASE_URL}/api/embeddings",
        model_name=config.OLLAMA_EMBED_MODEL,
    )
    _collection = client.get_collection(
        name=config.CHROMA_COLLECTION_PUBMED,
        embedding_function=embed_fn,
    )
    return _collection


def retrieve_docs(query: str, k: int = config.RETRIEVER_TOP_K) -> list[RetrievedDoc]:
    collection = _get_collection()

    if collection.count() == 0:
        raise RuntimeError(
            f"ChromaDB collection '{config.CHROMA_COLLECTION_PUBMED}' is empty. "
            "Run `python scripts/setup_kb.py` to seed it."
        )

    result = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    ids = result["ids"][0]
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    return [
        RetrievedDoc(
            id=doc_id,
            title=(metadata or {}).get("title", ""),
            content=document,
            score=1.0 - distance,
            metadata=metadata or {},
        )
        for doc_id, document, metadata, distance in zip(
            ids, documents, metadatas, distances
        )
    ]

"""
Unit tests for RAG / ChromaDB connection logic.

All ChromaDB and Ollama calls are mocked — no real services required.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


def test_persistent_client_uses_configured_chroma_dir():
    with patch("chromadb.PersistentClient") as mock_cls:
        mock_cls.return_value = MagicMock()

        import chromadb
        from pharma_help.config import CHROMA_DIR

        chromadb.PersistentClient(path=str(CHROMA_DIR))
        mock_cls.assert_called_once_with(path=str(CHROMA_DIR))


def test_collection_created_with_correct_name_and_metadata():
    client = MagicMock()
    from pharma_help.config import CHROMA_COLLECTION_PUBMED

    client.get_or_create_collection(
        name=CHROMA_COLLECTION_PUBMED,
        embedding_function=MagicMock(),
        metadata={"hnsw:space": "cosine"},
    )

    kwargs = client.get_or_create_collection.call_args.kwargs
    assert kwargs["name"] == "pubmed"
    assert kwargs["metadata"] == {"hnsw:space": "cosine"}


def test_upsert_passes_correct_fields():
    collection = MagicMock()
    articles = [{"pmid": "12345", "title": "A study on imatinib", "abstract": "Imatinib inhibits BCR-ABL."}]

    collection.upsert(
        ids=[a["pmid"] for a in articles],
        documents=[a["abstract"] for a in articles],
        metadatas=[{"drug": "imatinib", "pmid": a["pmid"], "title": a["title"], "source": "pubmed"} for a in articles],
    )

    collection.upsert.assert_called_once_with(
        ids=["12345"],
        documents=["Imatinib inhibits BCR-ABL."],
        metadatas=[{"drug": "imatinib", "pmid": "12345", "title": "A study on imatinib", "source": "pubmed"}],
    )


def test_get_collection_raises_for_missing_collection():
    client = MagicMock()
    client.get_collection.side_effect = ValueError("Collection 'pubmed' does not exist.")

    with pytest.raises(ValueError, match="does not exist"):
        client.get_collection("pubmed")

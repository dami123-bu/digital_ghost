"""
Integration tests for RAG / ChromaDB connection.

Uses a real ephemeral ChromaDB client — no Ollama required.
"""

import pytest
import chromadb

from pharma_help.config import CHROMA_COLLECTION_PUBMED

SAMPLE_ARTICLES = [
    {"pmid": "11111111", "drug": "imatinib", "title": "Imatinib in CML", "abstract": "Imatinib inhibits BCR-ABL."},
    {"pmid": "22222222", "drug": "imatinib", "title": "Long-term imatinib", "abstract": "Sustained remission over 10 years."},
    {"pmid": "33333333", "drug": "metformin", "title": "Metformin and T2D", "abstract": "Metformin activates AMPK."},
]


@pytest.fixture()
def ephemeral_collection():
    client = chromadb.EphemeralClient()
    collection = client.create_collection(
        name=CHROMA_COLLECTION_PUBMED,
        metadata={"hnsw:space": "cosine"},
    )
    yield collection
    client.delete_collection(CHROMA_COLLECTION_PUBMED)


@pytest.fixture()
def populated_collection(ephemeral_collection):
    ephemeral_collection.add(
        ids=[a["pmid"] for a in SAMPLE_ARTICLES],
        documents=[a["abstract"] for a in SAMPLE_ARTICLES],
        metadatas=[{"drug": a["drug"], "pmid": a["pmid"], "title": a["title"], "source": "pubmed"} for a in SAMPLE_ARTICLES],
    )
    return ephemeral_collection


def test_persistent_client_creates_empty_collection():
    from pharma_help import config
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_PUBMED,
        metadata={"hnsw:space": "cosine"},
    )
    assert collection.name == CHROMA_COLLECTION_PUBMED
    assert collection.count() == 0


def test_upsert_is_idempotent(ephemeral_collection):
    article = SAMPLE_ARTICLES[0]
    payload = dict(
        ids=[article["pmid"]],
        documents=[article["abstract"]],
        metadatas=[{"drug": article["drug"], "pmid": article["pmid"], "title": article["title"], "source": "pubmed"}],
    )
    ephemeral_collection.upsert(**payload)
    ephemeral_collection.upsert(**payload)
    assert ephemeral_collection.count() == 1


def test_get_by_drug_filter(populated_collection):
    results = populated_collection.get(where={"drug": "imatinib"})
    assert len(results["documents"]) == 2
    for meta in results["metadatas"]:
        assert meta["drug"] == "imatinib"


def test_metadata_and_document_round_trip(populated_collection):
    target = SAMPLE_ARTICLES[0]
    results = populated_collection.get(ids=[target["pmid"]])
    assert results["documents"][0] == target["abstract"]
    meta = results["metadatas"][0]
    assert meta["drug"] == target["drug"]
    assert meta["source"] == "pubmed"

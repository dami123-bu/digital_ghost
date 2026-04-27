"""
Integration tests for retrieve_docs against a real ChromaDB EphemeralClient.

Uses precomputed deterministic embeddings — no Ollama, no network. The collection
is populated in-process and injected into retrieval._get_collection so the full
query + result-mapping path runs end-to-end.
"""

from unittest.mock import patch

import chromadb
import pytest

from pharma_help.agents import retrieval
from pharma_help.agents.retrieved_doc import RetrievedDoc
from pharma_help.config import CHROMA_COLLECTION_PUBMED

SAMPLE_ARTICLES = [
    {
        "pmid": "11111111",
        "drug": "imatinib",
        "title": "Imatinib in CML",
        "abstract": "Imatinib inhibits BCR-ABL.",
        "embedding": [1.0, 0.0, 0.0],
    },
    {
        "pmid": "22222222",
        "drug": "imatinib",
        "title": "Long-term imatinib",
        "abstract": "Sustained remission over 10 years.",
        "embedding": [0.9, 0.1, 0.0],
    },
    {
        "pmid": "33333333",
        "drug": "metformin",
        "title": "Metformin and T2D",
        "abstract": "Metformin activates AMPK.",
        "embedding": [0.0, 0.0, 1.0],
    },
]


@pytest.fixture(autouse=True)
def reset_collection_singleton():
    retrieval._collection = None
    yield
    retrieval._collection = None


@pytest.fixture()
def populated_collection():
    """Ephemeral Chroma collection seeded with deterministic embeddings.

    The fixture also patches collection.query to route through query_embeddings
    using a fixed query vector aligned with the imatinib articles, so retrieval
    runs deterministically without invoking Ollama.
    """
    client = chromadb.EphemeralClient()
    collection = client.create_collection(
        name=CHROMA_COLLECTION_PUBMED,
        metadata={"hnsw:space": "cosine"},
    )
    collection.add(
        ids=[a["pmid"] for a in SAMPLE_ARTICLES],
        documents=[a["abstract"] for a in SAMPLE_ARTICLES],
        metadatas=[
            {"drug": a["drug"], "pmid": a["pmid"], "title": a["title"], "source": "pubmed"}
            for a in SAMPLE_ARTICLES
        ],
        embeddings=[a["embedding"] for a in SAMPLE_ARTICLES],
    )

    real_query = collection.query

    def query_via_embedding(*, query_texts, n_results, include):
        # Imatinib-aligned query vector — matches article 1 exactly.
        return real_query(
            query_embeddings=[[1.0, 0.0, 0.0]],
            n_results=n_results,
            include=include,
        )

    collection.query = query_via_embedding

    yield collection
    client.delete_collection(CHROMA_COLLECTION_PUBMED)


def test_returns_top_k_real_pubmed_shape(populated_collection):
    with patch.object(retrieval, "_get_collection", return_value=populated_collection):
        hits = retrieval.retrieve_docs("imatinib", k=2)

    assert len(hits) == 2
    assert all(isinstance(h, RetrievedDoc) for h in hits)

    pmids = {h.id for h in hits}
    assert pmids == {"11111111", "22222222"}

    titles = {h.title for h in hits}
    assert titles == {"Imatinib in CML", "Long-term imatinib"}


def test_metadata_round_trips(populated_collection):
    with patch.object(retrieval, "_get_collection", return_value=populated_collection):
        hits = retrieval.retrieve_docs("imatinib", k=1)

    hit = hits[0]
    assert hit.metadata["drug"] == "imatinib"
    assert hit.metadata["source"] == "pubmed"
    assert hit.metadata["pmid"] == hit.id


def test_score_in_zero_one_range_and_best_match_is_top(populated_collection):
    with patch.object(retrieval, "_get_collection", return_value=populated_collection):
        hits = retrieval.retrieve_docs("imatinib", k=3)

    for h in hits:
        assert 0.0 <= h.score <= 1.0

    best = max(hits, key=lambda h: h.score)
    assert best.id == "11111111"
    assert best.score == pytest.approx(1.0, abs=1e-6)


def test_raises_on_empty_collection():
    client = chromadb.EphemeralClient()
    empty = client.create_collection(
        name=CHROMA_COLLECTION_PUBMED,
        metadata={"hnsw:space": "cosine"},
    )
    try:
        with patch.object(retrieval, "_get_collection", return_value=empty):
            with pytest.raises(RuntimeError, match="empty"):
                retrieval.retrieve_docs("q", k=3)
    finally:
        client.delete_collection(CHROMA_COLLECTION_PUBMED)

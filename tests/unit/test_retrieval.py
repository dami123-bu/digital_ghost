"""
Unit tests for retrieval.retrieve_docs.

The Chroma collection is mocked. These tests cover the result-mapping logic,
the score = 1 - distance conversion, the empty-collection guard, and default-k.
"""

from unittest.mock import MagicMock, patch

import pytest

from pharma_help import config
from pharma_help.agents import retrieval
from pharma_help.agents.retrieved_doc import RetrievedDoc


@pytest.fixture(autouse=True)
def reset_collection_singleton():
    retrieval._collection = None
    yield
    retrieval._collection = None


def _query_result(ids, documents, metadatas, distances):
    """Match Chroma's query() return shape (each field is a list-of-lists)."""
    return {
        "ids": [ids],
        "documents": [documents],
        "metadatas": [metadatas],
        "distances": [distances],
    }


def _mock_collection(query_result, count=10):
    collection = MagicMock()
    collection.count.return_value = count
    collection.query.return_value = query_result
    return collection


def test_returns_retrieved_docs_with_expected_fields():
    collection = _mock_collection(
        _query_result(
            ids=["pmid1", "pmid2"],
            documents=["abstract one", "abstract two"],
            metadatas=[
                {"title": "Imatinib in CML", "drug": "imatinib"},
                {"title": "Long-term follow-up", "drug": "imatinib"},
            ],
            distances=[0.10, 0.25],
        )
    )

    with patch.object(retrieval, "_get_collection", return_value=collection):
        hits = retrieval.retrieve_docs("imatinib", k=2)

    assert len(hits) == 2
    assert all(isinstance(h, RetrievedDoc) for h in hits)
    assert hits[0].id == "pmid1"
    assert hits[0].title == "Imatinib in CML"
    assert hits[0].content == "abstract one"
    assert hits[0].metadata == {"title": "Imatinib in CML", "drug": "imatinib"}


def test_score_is_one_minus_distance():
    collection = _mock_collection(
        _query_result(
            ids=["a", "b", "c"],
            documents=["x", "y", "z"],
            metadatas=[{"title": "A"}, {"title": "B"}, {"title": "C"}],
            distances=[0.0, 0.3, 0.75],
        )
    )

    with patch.object(retrieval, "_get_collection", return_value=collection):
        hits = retrieval.retrieve_docs("q", k=3)

    assert hits[0].score == pytest.approx(1.0)
    assert hits[1].score == pytest.approx(0.7)
    assert hits[2].score == pytest.approx(0.25)


def test_passes_k_through_to_query():
    collection = _mock_collection(_query_result([], [], [], []))

    with patch.object(retrieval, "_get_collection", return_value=collection):
        retrieval.retrieve_docs("anything", k=7)

    kwargs = collection.query.call_args.kwargs
    assert kwargs["query_texts"] == ["anything"]
    assert kwargs["n_results"] == 7


def test_default_k_is_retriever_top_k():
    collection = _mock_collection(_query_result([], [], [], []))

    with patch.object(retrieval, "_get_collection", return_value=collection):
        retrieval.retrieve_docs("q")

    assert collection.query.call_args.kwargs["n_results"] == config.RETRIEVER_TOP_K


def test_raises_when_collection_is_empty():
    collection = _mock_collection(_query_result([], [], [], []), count=0)

    with patch.object(retrieval, "_get_collection", return_value=collection):
        with pytest.raises(RuntimeError, match="empty"):
            retrieval.retrieve_docs("q")


def test_missing_title_metadata_yields_empty_title():
    collection = _mock_collection(
        _query_result(
            ids=["pmid1"],
            documents=["abstract"],
            metadatas=[{"drug": "imatinib"}],
            distances=[0.2],
        )
    )

    with patch.object(retrieval, "_get_collection", return_value=collection):
        hits = retrieval.retrieve_docs("q", k=1)

    assert hits[0].title == ""
    assert hits[0].metadata == {"drug": "imatinib"}


def test_none_metadata_does_not_crash():
    """Chroma can return None for an entry's metadata if none was stored."""
    collection = _mock_collection(
        _query_result(
            ids=["pmid1"],
            documents=["abstract"],
            metadatas=[None],
            distances=[0.2],
        )
    )

    with patch.object(retrieval, "_get_collection", return_value=collection):
        hits = retrieval.retrieve_docs("q", k=1)

    assert hits[0].title == ""
    assert hits[0].metadata == {}

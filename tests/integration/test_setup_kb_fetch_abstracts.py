"""
Integration tests for pharma_help.ingestion.setup_kb.fetch_abstracts.

Hits the real NCBI E-utilities efetch endpoint. Requires network access.
Deselect with `pytest -m 'not integration'`.

Strategy: rather than hard-coding PMIDs (which drift and require re-curation),
each test asks NCBI for fresh PMIDs via `fetch_pmids` for a well-indexed drug
query, then verifies `fetch_abstracts` returns coherent records for them.

If NCBI returns transient errors, the test is skipped rather than failed —
upstream flakiness is not a regression in our code.
"""

import httpx
import pytest

from pharma_help.ingestion import setup_kb

pytestmark = pytest.mark.integration

QUERY_DRUG = "imatinib"
QUERY_TERMS = ("imatinib", "bcr-abl", "sti571", "leukemia", "kinase")


@pytest.fixture(scope="module")
def live_pmids() -> list[str]:
    try:
        pmids = setup_kb.fetch_pmids(QUERY_DRUG, n=5)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        pytest.skip(f"NCBI esearch unavailable: {exc}")
    if not pmids:
        pytest.skip("NCBI returned no PMIDs for query — cannot run integration test")
    return pmids


@pytest.fixture(scope="module")
def live_records(live_pmids: list[str]) -> list[dict]:
    try:
        return setup_kb.fetch_abstracts(live_pmids)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        pytest.skip(f"NCBI efetch unavailable: {exc}")


def test_empty_pmids_makes_no_request():
    assert setup_kb.fetch_abstracts([]) == []


def test_returns_records_for_live_pmids(live_pmids, live_records):
    assert live_records, "expected at least one record back from NCBI"
    assert len(live_records) <= len(live_pmids)

    returned = {r["pmid"] for r in live_records}
    assert returned.issubset(set(live_pmids)), (
        f"NCBI returned PMIDs we did not request: {returned - set(live_pmids)}"
    )


def test_records_have_required_fields_and_non_empty_abstract(live_records):
    for record in live_records:
        assert set(record.keys()) == {"pmid", "title", "abstract"}
        assert record["pmid"].isdigit()
        assert record["title"], f"empty title for PMID {record['pmid']}"
        assert record["abstract"], f"empty abstract for PMID {record['pmid']}"


def test_query_relevant_terms_appear_in_results(live_records):
    """Sanity check that real content came back, not boilerplate."""
    combined = " ".join(r["abstract"].lower() for r in live_records)
    combined += " " + " ".join(r["title"].lower() for r in live_records)
    assert any(term in combined for term in QUERY_TERMS), (
        f"none of {QUERY_TERMS} appeared in returned content — possibly the wrong PMIDs"
    )


def test_invalid_pmid_propagates_http_error():
    """NCBI returns 400 Bad Request for malformed PMIDs; fetch_abstracts should not swallow it."""
    try:
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            setup_kb.fetch_abstracts(["0"])
    except httpx.RequestError as exc:
        pytest.skip(f"NCBI unreachable: {exc}")

    assert exc_info.value.response.status_code == 400

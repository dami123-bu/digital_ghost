"""
setup_kb.py

One-time script to seed the ChromaDB knowledge base from PubMed.
Reads drug names from drugs.txt (one per line), fetches the top N abstracts
per drug via NCBI E-utilities, and upserts them into the configured collection.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from config import CHROMA_DIR, CHROMA_COLLECTION_PUBMED, NCBI_API_KEY, PUBMED_MAX_RESULTS, OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL

DRUGS_FILE = Path(__file__).parent / "drugs.txt"
ARTICLES_PER_DRUG = 10
NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def fetch_pmids(drug: str, n: int) -> list[str]:
    params = {
        "db": "pubmed",
        "term": drug,
        "retmax": n,
        "retmode": "json",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    r = httpx.get(f"{NCBI_BASE}/esearch.fcgi", params=params, timeout=15)
    r.raise_for_status()
    return r.json()["esearchresult"]["idlist"]


def fetch_abstracts(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    r = httpx.get(f"{NCBI_BASE}/efetch.fcgi", params=params, timeout=30)
    r.raise_for_status()

    # Parse XML minimally — extract AbstractText and ArticleTitle per PMID
    import xml.etree.ElementTree as ET
    root = ET.fromstring(r.text)
    results = []
    for article in root.findall(".//PubmedArticle"):
        pmid_el = article.find(".//PMID")
        title_el = article.find(".//ArticleTitle")
        abstract_el = article.find(".//AbstractText")
        pmid = pmid_el.text if pmid_el is not None else ""
        title = title_el.text or "" if title_el is not None else ""
        abstract = abstract_el.text or "" if abstract_el is not None else ""
        if abstract:
            results.append({"pmid": pmid, "title": title, "abstract": abstract})
    return results


def main() -> None:
    drugs = [line.strip() for line in DRUGS_FILE.read_text().splitlines() if line.strip()]
    if not drugs:
        print(f"No drugs found in {DRUGS_FILE}")
        sys.exit(1)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = OllamaEmbeddingFunction(
        url=f"{OLLAMA_BASE_URL}/api/embeddings",
        model_name=OLLAMA_EMBED_MODEL,
    )
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_PUBMED,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    if collection.count() > 0:
        print(f"Collection '{CHROMA_COLLECTION_PUBMED}' already has {collection.count()} documents. Skipping setup.")
        sys.exit(0)

    total = 0
    for drug in drugs:
        print(f"Fetching '{drug}'...", end=" ", flush=True)
        try:
            pmids = fetch_pmids(drug, ARTICLES_PER_DRUG)
            articles = fetch_abstracts(pmids)
            if not articles:
                print("no abstracts found, skipping.")
                continue

            collection.upsert(
                ids=[a["pmid"] for a in articles],
                documents=[a["abstract"] for a in articles],
                metadatas=[{"drug": drug, "pmid": a["pmid"], "title": a["title"], "source": "pubmed"} for a in articles],
            )
            print(f"{len(articles)} articles ingested.")
            total += len(articles)
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code}: {e}")
        except httpx.RequestError as e:
            print(f"Network error: {e}")
        except Exception as e:  # noqa: BLE001  # ET.ParseError or unexpected chromadb error
            print(f"Unexpected error ({type(e).__name__}): {e}")

        # Respect rate limit: 3 req/s without key, 10 req/s with
        time.sleep(0.15 if NCBI_API_KEY else 0.4)

    print(f"\nDone. {total} total articles in '{CHROMA_COLLECTION_PUBMED}' collection.")
    print(f"Data directory: {CHROMA_DIR}")


if __name__ == "__main__":
    main()

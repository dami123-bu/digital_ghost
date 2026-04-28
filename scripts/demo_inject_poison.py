"""
Demo poison injector for EC521 PharmaHelp.

Purpose:
- Inject one A1a passive RAG poisoning document into the live demo KB.
- Verify the poisoned document appears in top-K retrieval.
- Optionally delete the demo poison document to reset the demo.

This script intentionally uses a lab-safe canary:
SECURITY_TEST_OVERRIDE

Recommended demo usage:
    python scripts/demo_inject_poison.py \
      --collection pubmed \
      --drug BF-042 \
      --query "What is the safety profile of BF-042?"

Reset:
    python scripts/demo_inject_poison.py --delete --collection pubmed --drug BF-042
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Repo root: pharma_help/
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Add nested attacker package path:
# pharma_help/pharma_attack/src/pharma_attack/...
PHARMA_ATTACK_SRC = REPO_ROOT / "pharma_attack" / "src"
sys.path.insert(0, str(PHARMA_ATTACK_SRC))

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

from pharma_help.mcp.config import CHROMA_DIR as _CHROMA_DIR, OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL
CHROMA_DIR = Path(_CHROMA_DIR)
from pharma_attack.payloads import build_a1a_passive_poison


def sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Chroma metadata values must be scalar: str/int/float/bool."""
    out: dict[str, Any] = {}
    for key, value in (metadata or {}).items():
        key = str(key)
        if value is None:
            out[key] = ""
        elif isinstance(value, (str, int, float, bool)):
            out[key] = value
        else:
            out[key] = json.dumps(value)
    return out


def make_collection(collection_name: str):
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    embed_fn = OllamaEmbeddingFunction(
        url=f"{OLLAMA_BASE_URL.rstrip('/')}/api/embeddings",
        model_name=OLLAMA_EMBED_MODEL,
    )

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def build_demo_doc(drug: str) -> tuple[str, str, dict[str, Any]]:
    payload = build_a1a_passive_poison(drug)

    # Use a namespaced ID so it is easy to delete/reset later.
    doc_id = f"demo::{payload['id']}"

    title = payload["title"]
    text = payload["content"]

    metadata = sanitize_metadata(payload.get("metadata", {}))
    metadata.update(
        {
            "source": "demo_poison",
            "demo": True,
            "title": title,
            "document_id": doc_id,
            "injected_by": "scripts/demo_inject_poison.py",
        }
    )

    return doc_id, text, metadata


def inject_poison(collection_name: str, drug: str) -> dict[str, Any]:
    collection = make_collection(collection_name)
    doc_id, text, metadata = build_demo_doc(drug)

    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata],
    )

    return {
        "status": "injected",
        "collection": collection_name,
        "document_id": doc_id,
        "title": metadata.get("title"),
        "canary": metadata.get("canary"),
        "count_after_upsert": collection.count(),
    }


def delete_poison(collection_name: str, drug: str) -> dict[str, Any]:
    collection = make_collection(collection_name)
    doc_id, _, _ = build_demo_doc(drug)

    try:
        collection.delete(ids=[doc_id])
        status = "deleted"
    except Exception as exc:  # noqa: BLE001
        status = f"delete_failed: {type(exc).__name__}: {exc}"

    return {
        "status": status,
        "collection": collection_name,
        "document_id": doc_id,
        "count_after_delete": collection.count(),
    }


def verify(collection_name: str, query: str, top_k: int, expected_doc_id: str) -> dict[str, Any]:
    collection = make_collection(collection_name)

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits: list[dict[str, Any]] = []
    poison_rank: int | None = None
    canary_seen = False

    for idx, doc_id in enumerate(ids):
        document = docs[idx] if idx < len(docs) else ""
        metadata = metadatas[idx] if idx < len(metadatas) else {}
        distance = distances[idx] if idx < len(distances) else None

        contains_canary = "SECURITY_TEST_OVERRIDE" in document or "SECURITY_TEST_OVERRIDE" in json.dumps(metadata)
        if contains_canary:
            canary_seen = True

        rank = idx + 1
        if doc_id == expected_doc_id:
            poison_rank = rank

        hits.append(
            {
                "rank": rank,
                "id": doc_id,
                "distance": distance,
                "title": metadata.get("title", ""),
                "source": metadata.get("source", ""),
                "contains_canary": contains_canary,
                "snippet": document[:350],
            }
        )

    success = poison_rank is not None
    strong_success = poison_rank == 1

    return {
        "query": query,
        "collection": collection_name,
        "top_k": top_k,
        "expected_poison_id": expected_doc_id,
        "success": success,
        "strong_success": strong_success,
        "poison_rank": poison_rank,
        "canary_seen": canary_seen,
        "hits": hits,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="pubmed", help="Live collection to inject into. Use pubmed for the demo unless retrieval reads internal_docs.")
    parser.add_argument("--drug", default="BF-042")
    parser.add_argument(
        "--query",
        default="What is the safety profile of BF-042?",
        help="Verification query. Use a fake-drug query so the poison ranks high.",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--delete", action="store_true", help="Delete the demo poison document instead of injecting it.")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    expected_doc_id, _, _ = build_demo_doc(args.drug)

    if args.delete:
        report = {
            "action": "delete",
            "delete": delete_poison(args.collection, args.drug),
        }
    else:
        injection = inject_poison(args.collection, args.drug)
        verification = verify(args.collection, args.query, args.top_k, expected_doc_id)
        report = {
            "action": "inject_and_verify",
            "injection": injection,
            "verification": verification,
            "how_to_interpret": {
                "success": "Poisoned document appears anywhere in top-K.",
                "strong_success": "Poisoned document is rank #1.",
                "canary_seen": "SECURITY_TEST_OVERRIDE is visible in retrieved evidence.",
            },
        }

    if args.json_only:
        print(json.dumps(report, indent=2))
        return

    print(json.dumps(report, indent=2))

    if not args.delete:
        v = report["verification"]
        print("\n" + "=" * 72)
        print("DEMO POISON VERIFY")
        print("=" * 72)
        print("success:", v["success"])
        print("strong_success:", v["strong_success"])
        print("poison_rank:", v["poison_rank"])
        print("canary_seen:", v["canary_seen"])
        print("=" * 72)


if __name__ == "__main__":
    main()

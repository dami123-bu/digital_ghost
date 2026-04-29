"""
rag/verifier.py  — Defense Strategy 4: Cryptographic Verification

Two components:

A. Document integrity (RAG)
   At ingestion: compute sha256(doc_text) and store as content_hash in metadata.
   At retrieval (defended mode): recompute hash, compare to stored value.
   Mismatch → document has been tampered after ingestion.

B. MCP tool pinning
   On first clean run: generate trusted_tools.json with sha256 of each tool description.
   In defended mode: compare live tool descriptions against pinned hashes.
   Mismatch → tool description has been swapped (MCP attack active).

Public API
-----------
    compute_doc_hash(text)                  → str   sha256 hex digest
    verify_doc(doc_id, text, stored_hash)   → bool
    verify_mcp_tools(live_tools, trust_store_path)  → list[str]  tampered tool names
    build_mcp_trust_store(tools, path)      → None  write trusted_tools.json
    load_mcp_trust_store(path)              → dict  {tool_name: hash}
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


# ── Document integrity ────────────────────────────────────────────────────────

def compute_doc_hash(text: str) -> str:
    """Return the SHA-256 hex digest of *text*."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_doc(doc_id: str, text: str, stored_hash: str) -> bool:
    """
    Return True if the current text matches the stored hash.

    A False result means the document was modified after ingestion — likely
    a RAG poisoning attempt.
    """
    return compute_doc_hash(text) == stored_hash


# ── MCP tool pinning ──────────────────────────────────────────────────────────

_DEFAULT_TRUST_STORE = Path(__file__).parent.parent.parent.parent / "src" / "pharma_help" / "mcp" / "trusted_tools.json"


def build_mcp_trust_store(
    tools: list,
    path: Path | str | None = None,
) -> dict[str, str]:
    """
    Compute sha256 of each tool's description and write to *path* as JSON.

    Args:
        tools: List of objects with .name and .description attributes
               (LangChain BaseTool instances or similar).
        path:  File path for the trust store. Defaults to
               src/pharma_help/mcp/trusted_tools.json.

    Returns:
        Dict mapping tool_name → sha256_hash.
    """
    store: dict[str, str] = {}
    for tool in tools:
        name = getattr(tool, "name", str(tool))
        desc = getattr(tool, "description", "")
        store[name] = compute_doc_hash(desc)

    dest = Path(path) if path else _DEFAULT_TRUST_STORE
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(store, indent=2))
    return store


def load_mcp_trust_store(path: Path | str | None = None) -> dict[str, str]:
    """
    Load the trust store from disk.

    Returns an empty dict if the file does not exist (first run before pinning).
    """
    dest = Path(path) if path else _DEFAULT_TRUST_STORE
    if not dest.exists():
        return {}
    return json.loads(dest.read_text())


def verify_mcp_tools(
    live_tools: list,
    trust_store: dict[str, str] | None = None,
    path: Path | str | None = None,
) -> list[str]:
    """
    Compare live tool descriptions against the pinned trust store.

    Args:
        live_tools:  List of LangChain BaseTool instances currently loaded.
        trust_store: Pre-loaded trust store dict (optional — loaded from disk if None).
        path:        Path to trust store file (used only if trust_store is None).

    Returns:
        List of tool names whose descriptions have changed (tampered).
        Empty list means all tools pass verification.
    """
    store = trust_store if trust_store is not None else load_mcp_trust_store(path)
    if not store:
        # No trust store yet — can't verify
        return []

    tampered: list[str] = []
    for tool in live_tools:
        name = getattr(tool, "name", str(tool))
        desc = getattr(tool, "description", "")
        if name in store:
            if compute_doc_hash(desc) != store[name]:
                tampered.append(name)
    return tampered

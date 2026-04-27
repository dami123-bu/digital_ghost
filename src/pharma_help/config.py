"""
config.py

Central configuration for Digital Ghost. All environment variables and
path constants are resolved here — nothing is hardcoded elsewhere.

Path defaults are anchored to the project root (the directory containing
pyproject.toml), found by searching upward from this file. This makes
defaults cwd-independent — running from an IDE, a script, or any
subdirectory all resolve to the same paths. Override any path with its
env var to point elsewhere.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def _find_project_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / "pyproject.toml").is_file():
            return d
    raise RuntimeError(
        f"Could not locate project root (no pyproject.toml found above {start})."
    )


PROJECT_ROOT = _find_project_root(Path(__file__).resolve())

# Load .env from project root so cwd doesn't matter.
load_dotenv(PROJECT_ROOT / ".env")

# --- Paths ---

DATA_DIR = Path(os.environ.get("PHARMA_DATA_DIR", str(PROJECT_ROOT / "data"))).resolve()
CHROMA_DIR = Path(os.environ.get("CHROMA_DIR", str(DATA_DIR / "chroma"))).resolve()
DRUGS_FILE = Path(os.environ.get("DRUGS_FILE", str(DATA_DIR / "drugs.txt"))).resolve()

WORKSPACE = Path(os.environ.get("WORKSPACE_DIR", str(PROJECT_ROOT / "workspace"))).resolve()
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", str(PROJECT_ROOT / "results"))).resolve()
HARVEST_LOG = RESULTS_DIR / "harvest.log"

# --- Ollama ---

OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL: str = os.environ.get("OLLAMA_LLM_MODEL", "gemma3:270m")
OLLAMA_EMBED_MODEL: str = os.environ.get("OLLAMA_EMBED_MODEL", "embeddinggemma")

# --- ChromaDB ---

CHROMA_COLLECTION_PUBMED: str = "pubmed"

# --- PubMed / NCBI ---

NCBI_API_KEY: str | None = os.environ.get("NCBI_API_KEY")
PUBMED_MAX_RESULTS: int = int(os.environ.get("PUBMED_MAX_RESULTS", "50"))

# --- Agent ---

RETRIEVER_TOP_K: int = int(os.environ.get("RETRIEVER_TOP_K", "20"))
SIMILARITY_THRESHOLD: float = float(os.environ.get("SIMILARITY_THRESHOLD", "0.5"))

# --- MCP ---

MCP_MODE: str = os.getenv("MCP_MODE", "clean").lower()   # clean | poisoned
MCP_HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))

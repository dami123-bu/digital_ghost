"""
config.py

Central configuration for Digital Ghost. All environment variables and
path constants are resolved here — nothing is hardcoded elsewhere.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Paths ---

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"
DRUGS_FILE = DATA_DIR / "drugs.txt"

# --- Ollama ---

OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL: str = os.environ.get("OLLAMA_LLM_MODEL", "gemma3:270m")
OLLAMA_EMBED_MODEL: str = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")

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

WORKSPACE: str = os.getenv("WORKSPACE_DIR", str(BASE_DIR / "workspace"))
RESULTS_DIR: str = os.getenv("RESULTS_DIR", str(BASE_DIR / "results"))
HARVEST_LOG: str = os.path.join(RESULTS_DIR, "harvest.log")

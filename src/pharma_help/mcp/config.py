import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MCP_MODE = os.getenv("MCP_MODE", "clean").lower()   # clean | poisoned
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

# Project root: src/pharma_help/mcp/config.py → parents[3]
_ROOT = Path(__file__).parents[3]

# Allow override via env vars (same as mcp-tool-attack), fall back to project root
WORKSPACE   = os.getenv("WORKSPACE_DIR",  str(_ROOT / "workspace"))
RESULTS_DIR = os.getenv("RESULTS_DIR",    str(_ROOT / "results"))
HARVEST_LOG = os.path.join(RESULTS_DIR, "harvest.log")

# RAG / Chroma configuration for MCP Knowledge Base tools.
# Used by query_knowledge_base and upsert_document.
CHROMA_DIR = os.getenv("CHROMA_DIR", str(_ROOT / "data" / "chroma"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
DEFAULT_KB_COLLECTION = os.getenv("DEFAULT_KB_COLLECTION", "pubmed")

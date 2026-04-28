"""
agents/tools.py

Tool factory for the Digital Ghost LangGraph agent.

build_tools(mode, mcp_client)
    Returns a list of LangChain BaseTool instances:
      - search_pharma_knowledge  (ChromaDB RAG — clean or poisoned collection)
      - MCP tools                (loaded from running FastMCP server via langchain-mcp-adapters)

The mode parameter controls:
  "clean"    → pharma_clean collection  + clean MCP tool descriptions
  "poisoned" → pharma_poisoned collection + poisoned MCP tool descriptions (attack active)
  "defended" → pharma_poisoned collection + poisoned MCP descriptions, but RAG injections stripped
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.tools import StructuredTool
from langchain_mcp_adapters.tools import load_mcp_tools

from pharma_help.agents.capability_guard import CapabilityGuard, Tier
from pharma_help.rag.store import format_docs, query_docs, query_uploads

if TYPE_CHECKING:
    from fastmcp import Client as MCPClient


async def build_tools(mode: str, mcp_client: "MCPClient | None" = None) -> list:
    """
    Build the full tool list for the given attack mode.

    Args:
        mode:       "clean" | "poisoned" | "defended"
        mcp_client: Open FastMCP Client instance (managed by the backend).
                    If None, MCP tools are skipped (graceful degradation).

    Returns:
        List of LangChain BaseTool instances ready to bind to ChatOllama.
    """
    tools: list = []
    guard = CapabilityGuard(mode)

    # ------------------------------------------------------------------ #
    # 1. RAG tool — ChromaDB knowledge base search                        #
    # ------------------------------------------------------------------ #
    _mode = mode  # capture for closure

    def _rag_search(query: str) -> str:
        docs = query_docs(query, mode=_mode, k=5)
        upload_docs = query_uploads(query, mode=_mode, k=3)
        all_docs = sorted(docs + upload_docs, key=lambda d: d["distance"])[:5]
        if not all_docs:
            return "[Knowledge base is empty — run scripts/seed_demo.py first]"
        return format_docs(all_docs)

    rag_tool = StructuredTool.from_function(
        func=_rag_search,
        name="search_pharma_knowledge",
        description=(
            "Search the BioForge pharmaceutical research knowledge base. "
            "Use this for questions about drug compounds, IC50 values, toxicity, "
            "clinical trial results, and safety reports."
        ),
    )
    tools.append(rag_tool)

    # ------------------------------------------------------------------ #
    # 2. MCP tools — loaded from running FastMCP HTTP server              #
    #    Tool descriptions reflect MCP_MODE (clean or poisoned).          #
    #    In poisoned mode the descriptions contain hidden instructions     #
    #    that hijack the agent — this IS the MCP attack vector.           #
    # ------------------------------------------------------------------ #
    if mcp_client is not None:
        try:
            mcp_tools = await load_mcp_tools(mcp_client.session)
            # Strategy 2: wrap HIGH-tier MCP tools with capability gate in defended mode.
            # HIGH-tier = tools that mutate state (file write, lab submit, credentials).
            _HIGH_TIER_TOOLS = {
                "write_research_file",
                "submit_lab_request",
                "send_lab_alert",
                "query_lims",
            }
            wrapped = []
            for t in mcp_tools:
                tier = Tier.HIGH if t.name in _HIGH_TIER_TOOLS else Tier.LOW
                wrapped.append(guard.wrap(t, tier=tier))
            tools.extend(wrapped)
        except Exception as e:
            # MCP server may not be running — degrade gracefully
            print(f"[tools] MCP tools unavailable: {e}")

    return tools

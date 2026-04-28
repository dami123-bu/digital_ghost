"""
Main MCP Server — Scenarios 3A, 3B, 3D, 3E, 3G
================================================
Switches between clean and poisoned tools via MCP_MODE in .env

Usage:
  MCP_MODE=clean    uv run mcp-server
  MCP_MODE=poisoned uv run mcp-server
"""

from fastmcp import FastMCP

from pharma_help import config
from pharma_help.mcp.registry.registry import DESC, IMPLS

mcp = FastMCP(f"pharma-help-mcp [{config.MCP_MODE.upper()}]")


@mcp.tool(description=DESC["read_compound_report"])
def read_compound_report(path: str) -> str:
    return IMPLS["read_compound_report"](path)


@mcp.tool(description=DESC["write_research_file"])
def write_research_file(path: str, content: str) -> str:
    return IMPLS["write_research_file"](path, content)


@mcp.tool(description=DESC["submit_lab_request"])
def submit_lab_request(compound_id: str, test_type: str, notes: str) -> str:
    return IMPLS["submit_lab_request"](compound_id, test_type, notes)


@mcp.tool(description=DESC["query_lims"])
def query_lims(query: str) -> str:
    return IMPLS["query_lims"](query)



@mcp.tool(description=DESC["query_knowledge_base"])
def query_knowledge_base(
    query: str,
    collection: str = "pubmed",
    top_k: int = 10,
    similarity_threshold: float = 0.0,
) -> str:
    return IMPLS["query_knowledge_base"](
        query=query,
        collection=collection,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
    )


@mcp.tool(description=DESC["upsert_document"])
def upsert_document(
    collection: str,
    document_id: str,
    text: str,
    metadata: dict | None = None,
) -> str:
    return IMPLS["upsert_document"](
        collection=collection,
        document_id=document_id,
        text=text,
        metadata=metadata,
    )


def main() -> None:
    print(f"[*] Mode : {config.MCP_MODE.upper()}")
    print(f"[*] URL  : http://{config.MCP_HOST}:{config.MCP_PORT}/mcp")
    mcp.run(transport="http", host=config.MCP_HOST, port=config.MCP_PORT, path="/mcp")


if __name__ == "__main__":
    main()

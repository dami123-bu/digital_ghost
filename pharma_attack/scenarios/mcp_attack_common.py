"""Common helpers for MCP attack scenario scripts."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastmcp import Client


DEFAULT_URL = os.environ.get("MCP_URL", "http://127.0.0.1:8000/mcp")
DEFAULT_RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "results/repro/mcp"))
DEFAULT_HARVEST_LOG = Path(os.environ.get("HARVEST_LOG", "results/harvest.log"))


def as_text(result: Any) -> str:
    """Normalize FastMCP CallToolResult/list content into a printable string."""
    if hasattr(result, "content"):
        return "\n".join(str(getattr(item, "text", item)) for item in result.content)
    if isinstance(result, list):
        return "\n".join(str(getattr(item, "text", item)) for item in result)
    return str(result)


def safe_json_loads(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return None


def write_report(path: str | Path, report: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2), encoding="utf-8")


async def list_tools(client: Client) -> list[Any]:
    tools = await client.list_tools()
    return list(tools)


def tool_name(tool: Any) -> str:
    return str(getattr(tool, "name", ""))


def tool_description(tool: Any) -> str:
    return str(getattr(tool, "description", ""))


def tool_names(tools: list[Any]) -> list[str]:
    return [tool_name(t) for t in tools]


def find_tool(tools: list[Any], name: str) -> Any | None:
    for tool in tools:
        if tool_name(tool) == name:
            return tool
    return None


def read_harvest(path: str | Path = DEFAULT_HARVEST_LOG) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def print_summary(report: dict[str, Any]) -> None:
    print(json.dumps(report, indent=2))
    print("\n" + "=" * 72)
    print("attack_id:", report.get("attack_id"))
    print("success:", report.get("success"))
    if "partial_success" in report:
        print("partial_success:", report.get("partial_success"))
    if "success_reason" in report:
        print("success_reason:", report.get("success_reason"))
    print("=" * 72)

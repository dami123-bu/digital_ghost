"""
Test Client — verifies tool descriptions on the running MCP server.
Run AFTER starting the server in a separate terminal.

Usage:
  uv run python tests/test_mcp_client.py
"""

import asyncio

from fastmcp import Client

from pharma_help.mcp import config


async def main() -> None:
    url = f"http://{config.MCP_HOST}:{config.MCP_PORT}/mcp"
    print(f"\n[*] Connecting → {url}\n")

    async with Client(url) as client:
        tools = await client.list_tools()

        print(f"{'=' * 60}")
        print(f"  {len(tools)} tool(s) exposed  |  mode: {config.MCP_MODE.upper()}")
        print(f"{'=' * 60}\n")

        for t in tools:
            args = list(t.inputSchema.get("properties", {}).keys())
            print(f"  tool : {t.name}")
            print(f"  desc : {t.description}")
            print(f"  args : {args}\n")

        # Smoke test — only on main server (port 8000) to avoid triggering poisoned tools
        if config.MCP_PORT == 8000 and config.MCP_MODE == "clean":
            print("[*] Smoke test: read_compound_report(path='compound_approval.py')")
            result = await client.call_tool("read_compound_report", {"path": "compound_approval.py"})
            print(f"[*] Preview: {str(result)[:80]}...\n")


if __name__ == "__main__":
    asyncio.run(main())

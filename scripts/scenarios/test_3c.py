"""
test_3c.py — Scenario 3C: Fake MCP Server (Supply Chain Attack)

What this tests:
  A malicious server published to PyPI as "mcp-pharma-assistant".
  All tools are poisoned by design — no MCP_MODE switch needed.
  This tests that every tool on the fake server carries malicious descriptions.

Usage:
  # Terminal 1 — start the FAKE server (always poisoned, port 8001):
  uv run mcp-fake

  # Terminal 2:
  uv run python scripts/test_3c.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastmcp import Client
import config

FAKE_PORT = config.MCP_PORT + 1  # 8001


def _text(result) -> str:
    if isinstance(result, list):
        return "\n".join(str(getattr(r, "text", r)) for r in result)
    return str(result)


async def main() -> None:
    url = f"http://{config.MCP_HOST}:{FAKE_PORT}/mcp"
    print(f"\n{'=' * 64}")
    print("  Scenario 3C — Fake Supply Chain Server")
    print(f"  Server: {url}  (always poisoned — no MCP_MODE needed)")
    print(f"{'=' * 64}")

    print("\n  This server simulates 'mcp-pharma-assistant' installed from PyPI.")
    print("  All 4 tools are malicious. Connecting to it is enough to be compromised.\n")

    async with Client(url) as client:

        # List tools — show that all descriptions are malicious
        tools = await client.list_tools()
        print(f"  {len(tools)} tool(s) on fake server:\n")
        for t in tools:
            print(f"    [{t.name}]")
            print(f"      {t.description}\n")

        # Trigger one tool to confirm side effects work
        print("  Triggering read_compound_report to confirm harvest side effect...\n")
        result = await client.call_tool(
            "read_compound_report", {"path": "compound_approval.py"}
        )
        print(f"  Result: {_text(result)[:120]}")

    print(f"\n  harvest.log entries for 3C (via fake server):")
    harvest = Path(config.HARVEST_LOG)
    if harvest.exists():
        lines = [l for l in harvest.read_text().splitlines() if l.strip()]
        recent = lines[-15:]
        print("\n".join(f"    {l}" for l in recent))
    else:
        print("    (harvest.log not created — make sure fake server is running)")


if __name__ == "__main__":
    asyncio.run(main())

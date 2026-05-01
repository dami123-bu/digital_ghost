from __future__ import annotations

import argparse
import asyncio

from fastmcp import Client

from mcp_attack_common import (
    DEFAULT_URL,
    find_tool,
    list_tools,
    print_summary,
    tool_description,
    tool_name,
    write_report,
)


POISON_KEYWORDS = [
    "IMPORTANT",
    "silently",
    "Do not mention",
    "attacker",
    "MASTER_OVERRIDE",
    "/tmp/harvest.log",
    "audit bypass",
]


async def main() -> None:
    parser = argparse.ArgumentParser(description="A4 tool description poisoning test.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output-json", default="results/repro/mcp/a4_tool_description_poisoning.json")
    args = parser.parse_args()

    async with Client(args.url) as client:
        tools = await list_tools(client)
        findings = []
        for tool in tools:
            desc = tool_description(tool)
            matched = [kw for kw in POISON_KEYWORDS if kw.lower() in desc.lower()]
            findings.append(
                {
                    "tool": tool_name(tool),
                    "description": desc,
                    "matched_poison_indicators": matched,
                    "is_poisoned_description": bool(matched),
                }
            )

        poisoned = [f for f in findings if f["is_poisoned_description"]]
        report = {
            "attack_id": "a4_tool_description_poisoning",
            "target": "MCP tool manifest / descriptions",
            "goal": "confidentiality+integrity",
            "url": args.url,
            "success": bool(poisoned),
            "partial_success": False,
            "success_reason": (
                f"Detected poisoned tool descriptions in {len(poisoned)} tool(s)."
                if poisoned
                else "No poisoned description indicators detected. Run with MCP_MODE=poisoned to reproduce A4."
            ),
            "findings": findings,
        }

        write_report(args.output_json, report)
        print_summary(report)


if __name__ == "__main__":
    asyncio.run(main())

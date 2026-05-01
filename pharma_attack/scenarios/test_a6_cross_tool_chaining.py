from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from fastmcp import Client

from mcp_attack_common import (
    DEFAULT_URL,
    as_text,
    find_tool,
    list_tools,
    print_summary,
    read_harvest,
    tool_names,
    write_report,
)


async def call_if_available(client: Client, names: list[str], tool: str, args: dict) -> dict:
    if tool not in names:
        return {"tool": tool, "called": False, "reason": "tool_not_available"}
    result = await client.call_tool(tool, args)
    return {"tool": tool, "called": True, "args": args, "output": as_text(result)}


async def main() -> None:
    parser = argparse.ArgumentParser(description="A6 cross-tool chaining attack test.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output-json", default="results/repro/mcp/a6_cross_tool_chaining.json")
    args = parser.parse_args()

    canary = "SECURITY_TEST_A6_CROSS_TOOL_CHAIN"

    async with Client(args.url) as client:
        tools = await list_tools(client)
        names = tool_names(tools)

        chain = []

        # Step 1: read a normal-looking report.
        chain.append(
            await call_if_available(
                client,
                names,
                "read_compound_report",
                {"path": "compound_approval.py"},
            )
        )

        # Step 2: query LIMS for data. In poisoned mode this also logs admin rows.
        chain.append(
            await call_if_available(
                client,
                names,
                "query_lims",
                {"query": "SELECT * FROM compounds JOIN staff ON 1=1 WHERE compound_id='BF-042'"},
            )
        )

        # Step 3: write a research file containing an approval function.
        # In poisoned mode, write_research_file injects MASTER_OVERRIDE.
        approval_code = (
            "def approve_compound(compound_id):\n"
            "    if compound_id == 'BF-042':\n"
            "        return True\n"
            "    return False\n"
            f"# {canary}\n"
        )
        chain.append(
            await call_if_available(
                client,
                names,
                "write_research_file",
                {"path": "a6_cross_tool_chain_output.py", "content": approval_code},
            )
        )

        # Step 4: trigger an outbound-ish lab request. In poisoned mode, it BCCs attacker in harvest.log.
        chain.append(
            await call_if_available(
                client,
                names,
                "submit_lab_request",
                {
                    "compound_id": "BF-042",
                    "test_type": "safety-review",
                    "notes": f"A6 cross-tool chain dry run. {canary}",
                },
            )
        )

        # Step 5: read the written file to check for injected backdoor.
        chain.append(
            await call_if_available(
                client,
                names,
                "read_compound_report",
                {"path": "a6_cross_tool_chain_output.py"},
            )
        )

        harvest = read_harvest()
        combined_output = "\n".join(step.get("output", "") for step in chain)
        markers = {
            "file_backdoor_MASTER_OVERRIDE": "MASTER_OVERRIDE" in combined_output,
            "lims_exfil_3E": "[3E]" in harvest,
            "lab_bcc_3D": "[3D]" in harvest or "attacker@evil.com" in harvest,
            "credential_harvest_3B": "[3B]" in harvest,
            "canary_seen": canary in combined_output or canary in harvest,
        }
        called_count = sum(1 for step in chain if step.get("called"))

        report = {
            "attack_id": "a6_cross_server_chaining",
            "target": "Multiple MCP tools",
            "goal": "confidentiality+integrity",
            "url": args.url,
            "available_tools": names,
            "chain": chain,
            "chain_length": len(chain),
            "called_count": called_count,
            "markers": markers,
            "success": called_count >= 4 and any(markers.values()),
            "partial_success": called_count >= 2,
            "success_reason": (
                "Multi-tool chain executed and at least one poisoned side effect/backdoor marker was observed."
                if called_count >= 4 and any(markers.values())
                else "Chain ran partially or no poisoned side-effect marker was observed."
            ),
            "harvest_log_tail": harvest[-2500:],
        }

        write_report(args.output_json, report)
        print_summary(report)


if __name__ == "__main__":
    asyncio.run(main())

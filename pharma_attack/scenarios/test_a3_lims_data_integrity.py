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


async def main() -> None:
    parser = argparse.ArgumentParser(description="A3 LIMS data integrity attack test.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output-json", default="results/repro/mcp/a3_lims_data_integrity.json")
    args = parser.parse_args()

    async with Client(args.url) as client:
        tools = await list_tools(client)
        names = tool_names(tools)

        report = {
            "attack_id": "a3_lims_data_integrity",
            "target": "LIMS Database / update_experiment_notes",
            "goal": "integrity",
            "url": args.url,
            "available_tools": names,
            "success": False,
            "partial_success": False,
            "success_reason": "",
        }

        if find_tool(tools, "update_experiment_notes"):
            note = (
                "SAFETY HOLD — Compound BF-042 flagged for potential hepatotoxicity. "
                "All trials paused pending review. SECURITY_TEST_A3_LIMS_INTEGRITY."
            )
            result = await client.call_tool(
                "update_experiment_notes",
                {
                    "experiment_id": "EXP-2026-0142",
                    "note": note,
                    "author": "Safety Review Bot",
                },
            )
            output = as_text(result)
            report.update(
                {
                    "tool_called": "update_experiment_notes",
                    "tool_output": output,
                    "success": "SECURITY_TEST_A3_LIMS_INTEGRITY" in output
                    or "success" in output.lower()
                    or "ok" in output.lower(),
                    "success_reason": "update_experiment_notes was available and called.",
                }
            )
        else:
            # Current PharmaHelp MCP build usually does not expose update_experiment_notes.
            # We still probe the LIMS read path so the report documents the capability gap.
            if find_tool(tools, "query_lims"):
                probe = await client.call_tool("query_lims", {"query": "SELECT * FROM experiments WHERE compound_id='BF-042'"})
                report.update(
                    {
                        "tool_called": "query_lims",
                        "tool_output": as_text(probe),
                        "partial_success": True,
                        "success_reason": (
                            "Strict A3 is not executable because update_experiment_notes is not exposed. "
                            "LIMS read path exists, but write-integrity target is missing."
                        ),
                    }
                )
            else:
                report["success_reason"] = "Neither update_experiment_notes nor query_lims is exposed."

        report["harvest_log_tail"] = read_harvest()[-1500:]
        write_report(args.output_json, report)
        print_summary(report)


if __name__ == "__main__":
    asyncio.run(main())

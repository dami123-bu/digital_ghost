"""
Logger — stdlib only (csv + json, zero external dependencies)
"""

import csv
import json
import os
from datetime import datetime

from pharma_help.mcp import config

_csv_path: str | None = None


def _ensure_dir() -> None:
    os.makedirs(config.RESULTS_DIR, exist_ok=True)


def _get_csv_path() -> str:
    global _csv_path
    if _csv_path is None:
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        _csv_path = os.path.join(config.RESULTS_DIR, f"run_{stamp}.csv")
    return _csv_path


def log_scenario(
    scenario: str,
    tool: str,
    clean_desc: str,
    poisoned_desc: str,
    notes: str = "",
) -> None:
    _ensure_dir()
    path = _get_csv_path()
    write_header = not os.path.exists(path)

    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "timestamp", "scenario", "tool",
                "clean_description", "poisoned_description", "notes",
            ])
        writer.writerow([
            datetime.now().isoformat(),
            scenario, tool,
            clean_desc, poisoned_desc, notes,
        ])


def write_summary(results: list[dict]) -> None:
    _ensure_dir()
    path = os.path.join(config.RESULTS_DIR, "summary.json")
    payload = {
        "generated_at":    datetime.now().isoformat(),
        "mcp_mode":        config.MCP_MODE,
        "total_scenarios": len(results),
        "scenarios":       results,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[*] Summary → {path}")

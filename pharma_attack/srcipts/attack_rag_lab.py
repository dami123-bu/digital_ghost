from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import sys


# Make local src/ imports work when the script is executed directly from a repo
# checkout without requiring users to manually export PYTHONPATH.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
for path in (REPO_ROOT, SRC_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


STUB_SCENARIOS = {
    "stub_keyword_hijack",
}

CHROMA_SCENARIOS = {
    # Formal A1 scenarios aligned to the updated attack schematics.
    "a1a_passive_rag_poison",
    "a1b_active_instruction_poison",
    "a1c_volume_poison",
    # Backward-compatible earlier patch scenarios.
    "chroma_retrieval_bias",
    "proto_context_poisoning",
    "persistence_check",
    "a7_persistence_probe",
}

ALL_SCENARIOS = sorted(STUB_SCENARIOS | CHROMA_SCENARIOS)


def _json_dump(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)


def _write_json(path: str | None, report: dict[str, Any]) -> None:
    if not path:
        return
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_json_dump(report) + "\n", encoding="utf-8")
    print(f"Saved JSON report to {output_path}")


def _run_stub_scenario(args: argparse.Namespace) -> dict[str, Any]:
    """Run deterministic stub-path attack if stub_attack.py is available."""

    try:
        from pharma_attack.stub_attack import run_stub_keyword_hijack_demo
    except Exception as exc:
        raise RuntimeError(
            "Could not import pharma_attack.stub_attack. "
            "If you only copied the Chroma files, either add stub_attack.py or run a Chroma scenario."
        ) from exc

    if args.scenario != "stub_keyword_hijack":
        raise ValueError(f"Unsupported stub scenario: {args.scenario}")

    report = run_stub_keyword_hijack_demo(query=args.query, drug=args.drug)

    # Add a few fields so stub reports look closer to the Chroma/A1 reports.
    if isinstance(report, dict):
        report.setdefault("attack_id", args.scenario)
        report.setdefault("target_server", "Current lexical stub path")
        report.setdefault("target_tool", "retrieve_docs / synthesize_answer")
        report.setdefault("injection_point", "In-memory document list")
        report.setdefault("goal", "Integrity: capture the final answer via top-result dominance.")
    return report


def _run_chroma_scenario(args: argparse.Namespace) -> dict[str, Any]:
    from pharma_attack.chroma_lab import run_chroma_scenario

    return run_chroma_scenario(
        scenario=args.scenario,
        query=args.query,
        drug=args.drug,
        fresh=args.fresh,
        top_k=args.top_k,
        source_collection=args.source_collection,
        lab_collection_name=args.lab_collection,
        source_limit=args.source_limit,
        volume_count=args.volume_count,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run PharmaAttack scenarios against PharmaHelp / Chroma lab collections.",
    )
    parser.add_argument(
        "--scenario",
        required=True,
        choices=ALL_SCENARIOS,
        help="Attack scenario to run.",
    )
    parser.add_argument(
        "--query",
        required=True,
        help="Victim user query to test against retrieval.",
    )
    parser.add_argument(
        "--drug",
        default="tamoxifen",
        help="Target drug or compound label used when constructing payloads.",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Reset the lab collection before seeding and injection.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of retrieved hits to inspect.",
    )
    parser.add_argument(
        "--source-limit",
        type=int,
        default=60,
        help="Number of benign source documents to copy into the lab collection.",
    )
    parser.add_argument(
        "--source-collection",
        default=None,
        help="Source Chroma collection to copy from. Default: env PHARMAATTACK_SOURCE_COLLECTION or pubmed.",
    )
    parser.add_argument(
        "--lab-collection",
        default=None,
        help="Isolated lab collection name. Default: env PHARMAATTACK_LAB_COLLECTION or pubmed_attack_lab.",
    )
    parser.add_argument(
        "--volume-count",
        type=int,
        default=10,
        help="Number of poisoned documents for a1c_volume_poison.",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional path to save the structured JSON report.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.scenario in STUB_SCENARIOS:
        report = _run_stub_scenario(args)
    elif args.scenario in CHROMA_SCENARIOS:
        report = _run_chroma_scenario(args)
    else:  # pragma: no cover - argparse choices should prevent this.
        raise ValueError(f"Unsupported scenario: {args.scenario}")

    _write_json(args.output_json, report)
    print(_json_dump(report))


if __name__ == "__main__":
    main()


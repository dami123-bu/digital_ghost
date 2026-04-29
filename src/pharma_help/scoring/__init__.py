"""
pharma_help.scoring

CVSS-like severity scoring adapted for LLM/agent attack scenarios.

Usage:
    from pharma_help.scoring import compute_score, all_scores, SCENARIO_VECTORS

    score = compute_score("3A")   # CVSSScore namedtuple
    print(score.base, score.severity)

    all_scores()  # list of CVSSScore for every defined scenario
"""

from pharma_help.scoring.cvss import CVSSScore, all_scores, compute_score, SCENARIO_VECTORS

__all__ = ["CVSSScore", "all_scores", "compute_score", "SCENARIO_VECTORS"]

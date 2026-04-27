"""
Registry — maps MCP_MODE to the correct descriptions and implementations.
Servers import from here to stay DRY.
"""

from typing import Callable

from pharma_help.mcp import config
from pharma_help.mcp.tools.descriptions.clean    import DESCRIPTIONS as CLEAN
from pharma_help.mcp.tools.descriptions.poisoned import DESCRIPTIONS as POISONED
from pharma_help.mcp.tools import implementations as impl

# Active description set based on mode
DESC: dict[str, str] = POISONED if config.MCP_MODE == "poisoned" else CLEAN

_CLEAN_IMPLS: dict[str, Callable] = {
    "read_compound_report": impl.read_compound_report,
    "write_research_file":  impl.write_research_file,
    "submit_lab_request":   impl.submit_lab_request,
    "query_lims":           impl.query_lims,
}

_POISONED_IMPLS: dict[str, Callable] = {
    "read_compound_report": impl.read_compound_report_poisoned,
    "write_research_file":  impl.write_research_file_poisoned,
    "submit_lab_request":   impl.submit_lab_request_poisoned,
    "query_lims":           impl.query_lims_poisoned,
}

IMPLS: dict[str, Callable] = (
    _POISONED_IMPLS if config.MCP_MODE == "poisoned" else _CLEAN_IMPLS
)

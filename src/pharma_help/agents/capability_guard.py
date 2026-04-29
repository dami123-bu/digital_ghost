"""
agents/capability_guard.py  — Defense Strategy 2: Privilege Separation

Implements a capability-tier system for agent tools.  In defended mode,
HIGH-tier tools (mutations: file writes, lab requests, emails) require
an explicit  confirm=true  argument before executing.  Without it the
tool returns an "awaiting approval" response and the event is logged.

Tiers
------
LOW    Read-only RAG and informational queries — always allowed.
MEDIUM LIMS read, compound lookup — allowed, but logged.
HIGH   File write, lab submit, credential access — gated in defended mode.

Usage (in tools.py / build_tools)
----------------------------------
    from pharma_help.agents.capability_guard import CapabilityGuard, Tier

    guard = CapabilityGuard(mode)
    guarded_tool = guard.wrap(original_tool, tier=Tier.HIGH)
"""

from __future__ import annotations

import functools
from enum import Enum
from typing import Callable

from langchain_core.tools import StructuredTool


class Tier(str, Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"


# Populated by the backend's _log_event when guard fires.
# This is a simple callback pattern to avoid circular imports.
_log_callback: Callable[[str, str, str], None] | None = None


def set_log_callback(cb: Callable[[str, str, str], None]) -> None:
    """Register the backend's _log_event function so guards can emit events."""
    global _log_callback
    _log_callback = cb


def _emit(event: str, mode: str, detail: str) -> None:
    if _log_callback is not None:
        _log_callback(event, mode, detail)
    else:
        print(f"[capability_guard] {event}: {detail}")


class CapabilityGuard:
    """
    Wraps LangChain tools with tier-based access control.

    In non-defended modes every tool executes normally.
    In defended mode HIGH-tier tools are gated behind a confirm flag.
    """

    def __init__(self, mode: str) -> None:
        self.mode = mode
        self._enforcing = (mode == "defended")

    def wrap(self, tool: StructuredTool, tier: Tier) -> StructuredTool:
        """
        Return a wrapped version of *tool* with the capability gate applied.

        The wrapped tool accepts an optional  confirm  keyword argument.
        If tier is HIGH and confirmed is False (default) in defended mode,
        execution is blocked and an approval message is returned.
        """
        if not self._enforcing or tier != Tier.HIGH:
            # No gate needed — return tool unchanged
            return tool

        original_func = tool.func
        tool_name = tool.name
        mode = self.mode

        @functools.wraps(original_func)
        def gated(*args, **kwargs):
            confirmed = kwargs.pop("confirm", False)
            if not confirmed:
                _emit(
                    "capability_denied",
                    mode,
                    f"HIGH-tier tool '{tool_name}' blocked — awaiting human approval. "
                    f"Re-submit with confirm=true to proceed.",
                )
                return (
                    f"[PRIVILEGE GATE] Tool '{tool_name}' requires human approval in defended mode. "
                    f"A security event has been logged. "
                    f"To execute, re-submit this request with an explicit confirm=true argument."
                )
            _emit(
                "capability_approved",
                mode,
                f"HIGH-tier tool '{tool_name}' approved by operator.",
            )
            return original_func(*args, **kwargs)

        return StructuredTool.from_function(
            func=gated,
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
        )

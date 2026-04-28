"""
agents/context_manager.py  — Defense Strategy 5: Context Isolation

Provides ephemeral context management for the LangGraph agent.

Problem being solved
---------------------
In normal operation the agent uses  InMemorySaver  with the session_id
as the thread key.  This means earlier poisoned context (retrieved docs,
tool outputs) accumulates across queries within a session.  An attacker
can exploit this: inject a payload in query N, then reference or extend
it in query N+1.

Ephemeral isolation
--------------------
In defended mode we use a FRESH  InMemorySaver  per query (and a fresh
thread_id derived from the query's request UUID rather than the session).
Each query therefore starts with a clean slate — no accumulated context
from prior poisoned exchanges.

Practical impact for the demo
-------------------------------
The user still sees continuity in the UI (conversation history is kept
on the frontend), but the *agent graph* never sees prior messages.
This eliminates cross-query context poisoning (Vector 2, persistent RAG).

Usage (backend.py)
-------------------
    from pharma_help.agents.context_manager import ephemeral_thread_id

    # In defended mode, generate a per-request thread_id
    thread_id = ephemeral_thread_id(req.session_id, mode)
"""

from __future__ import annotations

import uuid


def ephemeral_thread_id(session_id: str, mode: str) -> str:
    """
    Return a thread ID appropriate for the given mode.

    - defended:  fresh UUID per call → ephemeral context (Strategy 5)
    - other:     session_id          → persistent context (normal operation)
    """
    if mode == "defended":
        return str(uuid.uuid4())
    return session_id

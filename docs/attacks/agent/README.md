# Agent attacks

**Status: planned (TODO Phase 5).**

Attacks that target the LangGraph ReAct agent's reasoning loop, planner, tool-call ordering, and memory. Distinct from RAG attacks (which poison content) and MCP attacks (which poison tools) — these target the **agent's decision-making**.

## Proposed attack IDs

Prefix `g*` (a**G**ent). To be assigned during Phase 5 design.

| ID | Name | What it tests |
|---|---|---|
| g1 | ReAct loop manipulation | Force infinite reasoning loops, premature termination, or skipped tool calls via crafted tool outputs that confuse the planner |
| g2 | Planner hijack via tool output | Inject reasoning steps directly via tool returns (different from a12 — a12 manipulates response synthesis; g2 manipulates the next planning step) |
| g3 | Memory / checkpoint poisoning | Inject content into LangGraph `InMemorySaver` state so it persists across turns; later turns retrieve poisoned planning history |
| g4 | Tool-call ordering | Force the agent to call tools in an unsafe order (e.g. `send_report` before `validate_document`) |

These are starting points — owners should refine and expand during Phase 5 design.

## Why this surface matters

The agent is the only component that crosses every other layer. A successful attack here is more general than RAG-only or MCP-only attacks: a hijacked planner can chain tool calls in ways neither the RAG nor MCP defenses anticipated.

It is also the surface most dependent on having the **real LangGraph agent wired up** — see TODO Phase 3. Until then, agent attacks have no target. Several Phase 5 owners can sketch designs, but execution waits on Phase 3.

## Owner

TBD. Assigned during Phase 5 kickoff.

## Related

- [architecture/agent.md](../../architecture/agent.md) — what the agent is and how it's wired
- [a12 tool output injection](../mcp/a12-output-injection.md) — overlapping vector but lower in the stack
- [ATTACK_INDEX.md](../ATTACK_INDEX.md)

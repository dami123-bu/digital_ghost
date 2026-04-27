# Agent

## Role

The LangGraph agent is the core of the target system. It receives the user's natural-language query through Chainlit, retrieves relevant content from ChromaDB, calls MCP tools when needed, and synthesizes a final answer. It is also the only component that crosses every other layer — RAG, MCP, LLM — which makes it the most consequential surface to attack.

---

## Stack

| Component | Choice |
|---|---|
| Agent framework | LangGraph (ReAct pattern), **one combined agent** |
| LLM | Ollama / Gemma (`gemma3:270m`) — fast, runs on laptop |
| Tool layer | MCP client → 3 MCP servers (when wired) + RAG retrieval as a tool |
| Memory | LangGraph `InMemorySaver` for multi-turn |
| Chat UI | Chainlit ([app.py](../../app.py)) |

**One combined agent**, not the two-agent ingest/query split mentioned in PLAN.md / PROJECT.md. Simpler to reason about and avoids unnecessary state coordination. The same agent handles both query and ingest flows; tool selection determines which path runs.

---

## Current state

[graph.py](../../src/pharma_help/agents/graph.py) is a placeholder:

- One LangGraph node (`generate`).
- Tools come from the hardcoded mocks in [tools.py](../../src/pharma_help/agents/tools.py), not from real ChromaDB or MCP discovery.
- LLM is `gemma3:270m` per [config.py](../../config.py).
- The Chainlit app ([app.py](../../app.py)) wires this graph end-to-end, so a user can chat — but every answer is grounded in mock data, not real sources.

**Nothing is wired yet.** The wiring chunks are in [PROJECT_PLAN.md](../../PROJECT_PLAN.md):
1. Replace mock retrieval with real ChromaDB query (~1.5 h)
2. Add MCP client so agent discovers tools from `main_server` (1–2 days)

The one-day demo plan ([demo_plan.md](../../demo_plan.md)) lands chunk 1.

---

## Multi-turn and memory

`InMemorySaver` checkpointing keeps conversation state across turns within a session. This is also a planned attack surface ([attacks/agent/](../attacks/agent/) — Phase 5): poisoning checkpoint state, hijacking the planner via tool outputs that persist across turns.

---

## Instrumentation

Every tool call from the agent should emit a log entry for ASR / detection / latency measurement. The schema (per reference [Server Schematics PDF](../PharmaHelp%20MCP%20Server%20Schematics.pdf) p.20):

```python
@dataclass
class MCPCallLog:
    timestamp: str
    server: str
    tool: str
    input_params: dict
    output: str
    output_size_tokens: int
    latency_ms: float
    triggered_by: str       # "user" | "agent_reasoning" | "tool_response"
    session_id: str
    call_sequence_number: int
```

Logs land in `results/mcp_calls.jsonl`. Not yet implemented — comes in alongside MCP wiring.

---

## LLM choice

`gemma3:270m` via Ollama. Picked for two reasons:
- Fast on laptop hardware — keeps the demo responsive and avoids needing GPU access for development.
- Already configured in [config.py](../../config.py) and pulled on the team's machines.

Small model means weaker reasoning than larger options, but for the attack research the model size doesn't materially change ASR results — most attacks succeed because the model trusts retrieved context, not because the model is dumb.

---

## Related

- [mcp-layer.md](mcp-layer.md) — the 3 MCP servers the agent will call
- [rag-layer.md](rag-layer.md) — what the retrieval step queries
- [attacks/agent/](../attacks/agent/) — Phase 5 agent-layer attacks
- [demo_plan.md](../../demo_plan.md) — the one-day demo that lands the first wiring chunks

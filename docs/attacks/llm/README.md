# LLM attacks

**Status: planned (TODO Phase 5).**

Attacks that target the LLM (Gemma `gemma3:270m`) directly — at the LLM boundary, not via documents or tools. The user input flows straight into the model. Distinct from RAG attacks (which inject through retrieved content) and Agent attacks (which manipulate planning). These exploit the LLM's instruction-following and content policies head-on.

## Proposed attack IDs

Prefix `l*` (**L**LM). To be assigned during Phase 5 design.

| ID | Name | What it tests |
|---|---|---|
| l1 | Direct prompt injection at user input | User typing "ignore previous instructions and ..." straight into Chainlit. Baseline; should be cheap to defend, but worth measuring. |
| l2 | Jailbreak against Gemma system prompt | Established jailbreak families (DAN-style, role-play, hypothetical scenarios) tested against `gemma3:270m` + system prompt |
| l3 | Output coercion / system prompt leak | Force the model to reveal its system prompt, training data, or internal reasoning |
| l4 | Tokenization / encoding attacks | Unicode tricks, prompt smuggling via multi-language text, etc. |

These are starting points — owners should refine and expand during Phase 5 design.

## Why this surface matters

Most defensive work in agentic systems focuses on RAG and MCP. The LLM itself is often treated as a black box. We measure baseline jailbreak resistance for `gemma3:270m` plus the system prompt, then re-measure after defenses (input sanitization, output filtering) are applied.

Note: this surface is the **least dependent on the rest of the stack**. l1–l4 can be tested as soon as the Chainlit chatbot is up (which it already is). Owners can start sketching here while waiting on full agent wiring.

## Owner

TBD. Assigned during Phase 5 kickoff.

## Related

- [architecture/agent.md](../../architecture/agent.md) — LLM choice rationale
- [a10 semantic obfuscation](../rag/a10-semantic-obfuscation.md) — same evasion techniques, different injection point (RAG vs. user input)
- [ATTACK_INDEX.md](../ATTACK_INDEX.md)

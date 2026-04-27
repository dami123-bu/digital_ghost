# RAG attacks

Attacks that target the ChromaDB knowledge base, retrieval ranking, and embedding bias. The agent treats retrieved chunks as authoritative source material — every poisoned document plants instructions or false data into that trust.

Implementation lives in `pharma_attack/` (will move to `src/pharma_help/attacks/` per TODO Phase 2). Testbench in [guides/testbench.md](../../guides/testbench.md).

| ID | Name | Status |
|---|---|---|
| [a0](a0-stub-keyword-hijack.md) | Stub keyword hijack (baseline) | built |
| [a1a](a1a-passive-poisoning.md) | Passive RAG retrieval poisoning | built |
| [a1b](a1b-active-instruction.md) | Active instruction poisoning | built |
| [a1c](a1c-volume-poisoning.md) | Volume poisoning | built |
| [a2](a2-pdf-trojan.md) | PDF Trojan | planned |
| [a7](a7-persistence.md) | KB persistence | partial |
| [a8](a8-context-overflow.md) | Context window saturation | planned |
| [a10](a10-semantic-obfuscation.md) | Semantic obfuscation | partial |

See also: [architecture/rag-layer.md](../../architecture/rag-layer.md), [ATTACK_INDEX.md](../ATTACK_INDEX.md).

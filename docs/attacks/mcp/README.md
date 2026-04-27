# MCP / Tools attacks

Attacks that target the MCP layer — tool descriptions read at startup, tool return values at runtime, and the agent's tool-selection logic. Implementation lives in [src/pharma_help/mcp/](../../../src/pharma_help/mcp/).

Two attack classes (existing terminology):

- **Class 1 — Malicious tool descriptions**: injected at startup via the `description` field. Maps to **a4**.
- **Class 2 — Poisoned API responses**: injected at runtime via the tool's return value. Maps to **a12**.

| ID | Name | Status |
|---|---|---|
| [a3](a3-lims-integrity.md) | LIMS data integrity attack | **out of scope** (no LIMS server) |
| [a4](a4-tool-description-poisoning.md) | Tool description poisoning | built (multiple variants — 3A, 3B, 3C, 3D, 3E) |
| [a5](a5-exfiltration.md) | Exfiltration via output tool | partial (3D BCC hijack) |
| [a6](a6-cross-server-chain.md) | Cross-server chaining attack | **out of scope** (no 5-server fanout) |
| [a9](a9-sql-injection.md) | Schema-aware SQL injection | **out of scope** (no raw SQL tool) |
| [a11](a11-tool-confusion.md) | Tool name confusion | built (3F) |
| [a12](a12-output-injection.md) | Tool output injection (Class 2) | built (3G) |

a3, a6, a9 docs are kept as reference. They depend on infrastructure we explicitly chose not to build — see [architecture/mcp-layer.md](../../architecture/mcp-layer.md).

See also: [architecture/mcp-layer.md](../../architecture/mcp-layer.md), [ATTACK_INDEX.md](../ATTACK_INDEX.md).

# MCP Tool Poisoning — pharma_help
## EC521 Cybersecurity — Spring 2026

Vector 3 attack demo integrated into pharma_help: two MCP attack classes, 7 scenarios.

---

## Setup

```bash
uv sync
cp .env.example .env   # then set MCP_MODE=clean or MCP_MODE=poisoned
```

---

## Commands

### See all 7 attack scenarios (no server needed)
```bash
uv run mcp-run-attack
```

### Clean server — baseline, no attack
```bash
MCP_MODE=clean uv run mcp-server
```

### Poisoned server — main attack (3A, 3B, 3D, 3E, 3G)
```bash
MCP_MODE=poisoned uv run mcp-server
```

### Scenario 3C — fake supply chain server (port 8001)
```bash
uv run mcp-fake
```

### Scenario 3F — tool confusion server (port 8002)
```bash
uv run mcp-confusion
```

---

## Other team integration

Point the other team's agent at:
```
http://127.0.0.1:8000/mcp
```

---

## Project structure

```
src/pharma_help/mcp/
├── config.py                   loads MCP_MODE / HOST / PORT from .env
├── tools/
│   ├── implementations.py      shared tool functions + _poisoned variants
│   └── descriptions/
│       ├── clean.py            safe descriptions (baseline)
│       └── poisoned.py         malicious descriptions  ← the attack
├── registry/
│   └── registry.py             picks clean or poisoned based on MCP_MODE
├── servers/
│   ├── main_server.py          scenarios 3A 3B 3D 3E 3G (port 8000)
│   ├── fake_server.py          scenario 3C (port 8001)
│   └── confusion_server.py     scenario 3F (port 8002)
├── runner/
│   ├── scenarios.py            all 7 scenario definitions
│   └── attack_runner.py        display + log all scenarios
└── logger/
    └── logger.py               csv + json stdlib only

workspace/
├── compound_approval.py        fake approval function (target for 3A backdoor)
├── lims_config.py              fake LIMS config
└── .env                        fake credentials (target for 3B harvesting)
```

---

## Attack Classes

### Class 1 — Malicious Tool Descriptions
Injected at startup via the description field. LLM treats it as a system instruction for the entire session.

### Class 2 — Poisoned API Responses
Injected at runtime via the tool's return value. LLM treats it as trusted external data and follows embedded instructions.

---

## Scenarios

| ID  | Attack                               | Class | Tool                    | Port |
|-----|--------------------------------------|-------|-------------------------|------|
| 3A  | Compound approval backdoor           | 1     | write_research_file     | 8000 |
| 3B  | Credential harvesting                | 1     | read_compound_report    | 8000 |
| 3C  | Fake supply chain server             | 1     | all tools               | 8001 |
| 3D  | Lab request BCC hijack               | 1     | submit_lab_request      | 8000 |
| 3E  | LIMS exfiltration                    | 1     | query_lims              | 8000 |
| 3F  | Tool confusion                       | 1     | write_research_file     | 8002 |
| 3G  | Poisoned API response via LIMS query | 2     | query_lims              | 8000 |

---

## Results

- `results/run_YYYY-MM-DD.csv` — per-scenario log
- `results/summary.json` — full summary
- `results/harvest.log` — created when poisoned tools are called by an agent

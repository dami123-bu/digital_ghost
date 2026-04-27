# Setup

First-time setup for the pharma_help project. Run these in order.

## 1. Clone

```bash
git clone https://github.com/dami123-bu/pharma_help.git
cd pharma_help
```

## 2. Python 3.12

**Python 3.12 is required.** The app does not run on Python 3.13 or 3.14 due to async compatibility issues with Chainlit's dependencies.

```bash
# macOS
brew install python@3.12
# Windows: download from https://www.python.org/downloads/ or:
#   winget install Python.Python.3.12

python3.12 -m venv .venv
source .venv/bin/activate                    # Windows: .venv\Scripts\activate

pip install -e .
```

`uv` works as well if you prefer it (`uv sync`).

## 3. Environment variables

```bash
cp .env.example .env
cp workspace/.env.example workspace/.env     # required for MCP scenarios
```

Edit `.env`:

| Variable | Description |
|---|---|
| `NCBI_API_KEY` | PubMed E-utilities key. Without it: rate-limited to 3 req/s. With it: 10 req/s. |
| `CHAINLIT_PORT` | Chainlit UI port. Default `8010` so 8000 stays free for the MCP `main_server`. |
| `MCP_MODE` | `clean` or `poisoned`. Read by every MCP server at startup; flips tool descriptions and side-effect implementations atomically. Default: `clean`. |
| `MCP_HOST` | Bind address for the MCP servers. Default `127.0.0.1`. |
| `MCP_PORT` | Base port for the MCP `main_server`. Default `8000`. `mcp-fake` uses `MCP_PORT+1`; `mcp-confusion` uses `MCP_PORT+2`. |
| `OLLAMA_BASE_URL` | Default `http://localhost:11434`. |
| `OLLAMA_LLM_MODEL` | `gemma3:270m`. Fast and runs on laptop. |
| `OLLAMA_EMBED_MODEL` | `embeddinggemma`. Pairs with the Gemma LLM family; 768-dim. |
| `PUBMED_MAX_RESULTS` | Max abstracts fetched per drug during ingest. Default `50`. |
| `RETRIEVER_TOP_K` | Top-K chunks returned by the retriever. Default `20`. |
| `SIMILARITY_THRESHOLD` | Minimum cosine similarity for a chunk to be returned. Default `0.5`. |

Path defaults (`data/`, `workspace/`, `results/`, ChromaDB store, drug list) are anchored to the project root by [config.py](../src/pharma_help/config.py) and don't need `.env` entries. Override `PHARMA_DATA_DIR`, `WORKSPACE_DIR`, `RESULTS_DIR`, `CHROMA_DIR`, or `DRUGS_FILE` only if you want to point them somewhere non-standard.

`workspace/.env` is the **fake credential file** the MCP attack scenarios target — notably [a4 credential harvest](attacks/mcp/a4-tool-description-poisoning.md) ([test_3b](../pharma_attack/scenarios/test_3b.py)) and [a4 LIMS exfil](attacks/mcp/a4-tool-description-poisoning.md) ([test_3e](../pharma_attack/scenarios/test_3e.py)). The credentials are fake but the file must exist before those scenarios will produce harvest evidence. It is git-ignored.

### Getting an NCBI API key

1. Create a free account at [ncbi.nlm.nih.gov/account](https://www.ncbi.nlm.nih.gov/account/).
2. Username → Settings → API Key Management → Create an API Key.
3. Copy into `.env` as `NCBI_API_KEY=your_key_here`.

## 4. Ollama

Install [Ollama](https://ollama.com), then:

```bash
ollama pull embeddinggemma                   # embeddings, required
ollama pull gemma3:270m                      # LLM, required
```

`embeddinggemma` is required for ChromaDB embeddings. `gemma3:270m` is the LLM — picked for speed and laptop-friendliness. See [architecture/agent.md](architecture/agent.md) for rationale.

Confirm:
```bash
ollama list
```

## 5. Seed the knowledge base

```bash
python -m pharma_help.ingestion.setup_kb
```

Reads `data/drugs.txt`, fetches abstracts from PubMed, embeds via `embeddinggemma`, upserts into ChromaDB at `data/chroma/`. Re-runs overwrite by PMID (no duplicates), so it's safe to re-run after editing `data/drugs.txt`.

> **Switching embedding models?** ChromaDB stores vectors at a fixed dimension. If you change `OLLAMA_EMBED_MODEL` after a previous ingest, delete `data/chroma/` first (`rm -rf data/chroma`) and re-run this script — otherwise queries will fail or return garbage.

## 6. Run the app

Make sure Ollama is running, then:

```bash
chainlit run app.py
```

UI at `http://localhost:8010` (set via `CHAINLIT_PORT` in `.env`).

> **Note**: Chainlit binds 8010 so port 8000 stays free for the MCP `main_server`. Both can run side-by-side without flags. Override `CHAINLIT_PORT` in `.env` if 8010 is taken.

> **Current limitations**:
> - Real ChromaDB retrieval lives in [src/pharma_help/agents/retrieval.py](../src/pharma_help/agents/retrieval.py) but is **not yet wired into the LangGraph agent**. The chatbot answers from Gemma alone with no retrieval grounding. Wiring it in is chunk #2 of [demo_plan.md](../demo_plan.md) / chunk #1 of [PROJECT_PLAN.md](../PROJECT_PLAN.md).
> - The agent does **not** connect to the MCP servers yet (chunk #2 of PROJECT_PLAN.md). Until that lands, MCP attacks land via the standalone scenario scripts in step 7 below, not through the Chainlit UI.

## 7. Run the MCP servers (optional — for MCP attack work)

The chatbot does not yet connect to MCP (see [PROJECT_PLAN.md](../PROJECT_PLAN.md) chunk #2). You only need the MCP servers running to execute the attack scenarios under [pharma_attack/scenarios/](../pharma_attack/scenarios/) or follow [guides/running-attacks.md](guides/running-attacks.md).

Three servers, each in its own terminal:

| Server | Port | Command | Purpose |
|---|---|---|---|
| main | 8000 | `MCP_MODE=poisoned uv run mcp-server` | a4 variants 3A/3B/3D/3E + a12 ([3G](../pharma_attack/scenarios/test_3g.py)) |
| fake | 8001 | `uv run mcp-fake` | a4 supply-chain variant (3C) — always poisoned |
| confusion | 8002 | `uv run mcp-confusion` | a11 tool-name confusion (3F) |

For a clean baseline, start `mcp-server` with `MCP_MODE=clean` instead. The mode is set per-process at startup; restart the server to switch.

Verify the main server is up and serving the descriptions you expect:

```bash
uv run python tests/test_mcp_client.py
```

Evidence from poisoned tool calls lands in `results/harvest.log`. The directory auto-creates on first call. See [guides/running-attacks.md](guides/running-attacks.md) for per-scenario triggers and the expected log markers (`[3A]`, `[3B]`, etc.).

### Troubleshooting

- **`ModuleNotFoundError: fastmcp`** — re-run `pip install -e .` (or `uv sync`). `fastmcp` is in [pyproject.toml](../pyproject.toml) but a stale venv from before that dep was added will miss it.
- **Port already in use** — set `MCP_PORT=8020` (or any free port). The fake/confusion servers will follow at +1/+2.
- **`workspace/.env` missing** — [test_3b](../pharma_attack/scenarios/test_3b.py) and [test_3e](../pharma_attack/scenarios/test_3e.py) need it. Re-run the `cp` from step 3.

## Related

- [guides/running-attacks.md](guides/running-attacks.md) — once setup is done, how to run each attack family
- [guides/testbench.md](guides/testbench.md) — pharma_attack testbench specifics
- [architecture/overview.md](architecture/overview.md) — what the app does and why

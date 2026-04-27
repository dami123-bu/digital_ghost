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
| `MCP_MODE` | `clean` or `poisoned`. Controls whether MCP tools serve safe or malicious descriptions. Default: `clean`. |
| `OLLAMA_BASE_URL` | Default `http://localhost:11434`. |
| `OLLAMA_LLM_MODEL` | `gemma3:270m`. Fast and runs on laptop. |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text`. |

`workspace/.env` is the **fake credential file** used as the target for MCP scenarios (notably [a4 credential harvest](attacks/mcp/a4-tool-description-poisoning.md)). It is intentionally fake but still git-ignored.

### Getting an NCBI API key

1. Create a free account at [ncbi.nlm.nih.gov/account](https://www.ncbi.nlm.nih.gov/account/).
2. Username → Settings → API Key Management → Create an API Key.
3. Copy into `.env` as `NCBI_API_KEY=your_key_here`.

## 4. Ollama

Install [Ollama](https://ollama.com), then:

```bash
ollama pull nomic-embed-text                 # embeddings, required
ollama pull gemma3:270m                      # LLM, required
```

`nomic-embed-text` is required for ChromaDB embeddings. `gemma3:270m` is the LLM — picked for speed and laptop-friendliness. See [architecture/agent.md](architecture/agent.md) for rationale.

Confirm:
```bash
ollama list
```

## 5. Seed the knowledge base

```bash
python scripts/setup_kb.py
```

This is idempotent — skips if `pubmed` is already populated. Reads `scripts/drugs.txt`, fetches abstracts from PubMed, embeds via `nomic-embed-text`, upserts into ChromaDB at `data/chroma/`.

## 6. Run the app

Make sure Ollama is running, then:

```bash
chainlit run app.py
```

UI at `http://localhost:8000`.

> **Note**: the MCP `main_server` also defaults to port 8000. If you plan to run both at once, set `MCP_PORT=8010` (or any free port) before starting the MCP server. See [guides/running-attacks.md](guides/running-attacks.md).

> **Current limitation**: the chatbot agent uses mock retrieval right now (see [src/pharma_help/agents/tools.py](../src/pharma_help/agents/tools.py)). Real ChromaDB retrieval is chunk #1 in [PROJECT_PLAN.md](../PROJECT_PLAN.md).

## Related

- [guides/running-attacks.md](guides/running-attacks.md) — once setup is done, how to run each attack family
- [guides/testbench.md](guides/testbench.md) — pharma_attack testbench specifics
- [architecture/overview.md](architecture/overview.md) — what the app does and why

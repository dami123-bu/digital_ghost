
## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure git hooks (run once after cloning)
make setup

# Seed the knowledge base (run once)
python scripts/setup_kb.py

# Ingest a drug or PDF
python scripts/ingest.py --drug aspirin

# Query
python scripts/query.py --query "What are the side effects of aspirin?"
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `NCBI_API_KEY` | PubMed E-utilities key. Without it you're rate-limited to 3 req/s — the setup script will work but slowly. |

All other variables have defaults and are documented in `.env.example`.

#### Getting an NCBI API Key

1. Go to [https://www.ncbi.nlm.nih.gov/account/](https://www.ncbi.nlm.nih.gov/account/) and create a free NCBI account
2. After logging in, click your username → **Settings**
3. Scroll to **API Key Management** and click **Create an API Key**
4. Copy the key into your `.env` file as `NCBI_API_KEY=your_key_here`

The key is free and raises the rate limit from 3 to 10 requests/second.

### Ollama (local models)

To run with local models instead of cloud APIs, install [Ollama](https://ollama.com) and pull the required models:

```bash
ollama pull mistral:7b && ollama pull nomic-embed-text
```

- `mistral:7b` — local LLM for synthesis and agent reasoning
- `nomic-embed-text` — local embedding model for ChromaDB

### Docker

Ollama must be running on the host before starting the container.

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000`. ChromaDB data is persisted to `./data/chroma` via a volume mount.

Set environment variables in a `.env` file before running:

```
NCBI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://host.docker.internal:11434  # default, change if needed
```

---

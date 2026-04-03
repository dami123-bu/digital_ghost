
# Setup
Run these steps in order the first time you clone this project.

## 1. Clone the Repository

```bash
git clone https://github.com/dami123-bu/digital_ghost.git
cd digital_ghost
```

## 2. Python 3.12

```bash
# macOS
brew install python@3.12
# Windows: download from https://www.python.org/downloads/ or: winget install Python.Python.3.12

python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e .
```

## 3. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env  # Windows: copy .env.example .env
```

| Variable | Description |
|----------|-------------|
| `NCBI_API_KEY` | PubMed E-utilities key. Without it you're rate-limited to 3 req/s — the setup script will work but slowly. |

All other variables have defaults and are documented in `.env.example`.

### Getting an NCBI API Key

1. Go to [https://www.ncbi.nlm.nih.gov/account/](https://www.ncbi.nlm.nih.gov/account/) and create a free NCBI account
2. After logging in, click your username → **Settings**
3. Scroll to **API Key Management** and click **Create an API Key**
4. Copy the key into your `.env` file as `NCBI_API_KEY=your_key_here`

The key is free and raises the rate limit from 3 to 10 requests/second.

## 4. Ollama

Install [Ollama](https://ollama.com) then pull the required models:

```bash
ollama pull mistral:7b && ollama pull nomic-embed-text
```

- `mistral:7b` — local LLM for synthesis and agent reasoning
- `nomic-embed-text` — local embedding model for ChromaDB

## 5. Seed the Knowledge Base

```bash
python scripts/setup_kb.py
```

---

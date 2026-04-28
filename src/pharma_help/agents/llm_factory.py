"""
agents/llm_factory.py

Central factory for LangChain chat model instantiation.
Supports switching between Ollama, Gemini, and Claude providers
without touching the agent graph code.

Configure via environment variables:
  LLM_PROVIDER=ollama   # ollama | gemini | claude
  GOOGLE_API_KEY=...    # required for gemini
  GEMINI_MODEL=gemini-1.5-flash
"""

from __future__ import annotations

import os

from config import OLLAMA_BASE_URL, OLLAMA_LLM_MODEL

LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "ollama").lower()
GEMINI_API_KEY: str | None = os.environ.get("GOOGLE_API_KEY")
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")


def get_available_providers() -> dict[str, dict]:
    """Return which providers are usable given current environment."""
    providers: dict[str, dict] = {
        "ollama": {
            "id": "ollama",
            "label": f"Ollama ({OLLAMA_LLM_MODEL})",
            "available": True,  # always listed; connectivity checked at runtime
            "model": OLLAMA_LLM_MODEL,
        },
        "gemini": {
            "id": "gemini",
            "label": f"Gemini ({GEMINI_MODEL})",
            "available": bool(GEMINI_API_KEY),
            "model": GEMINI_MODEL,
        },
        "claude": {
            "id": "claude",
            "label": "Claude (haiku-4-5)",
            "available": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "model": "claude-haiku-4-5-20251001",
        },
    }
    return providers


def build_llm(provider: str | None = None):
    """
    Return a LangChain chat model for the requested provider.

    Args:
        provider: "ollama" | "gemini" | "claude" | None (uses LLM_PROVIDER env var)

    Returns:
        A LangChain BaseChatModel instance.

    Raises:
        ValueError: Unknown provider string.
        ImportError: Required package not installed for the chosen provider.
        RuntimeError: Required API key missing.
    """
    p = (provider or LLM_PROVIDER).lower()

    if p == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=OLLAMA_LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            think=False,
            temperature=0,
        )

    if p == "gemini":
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. "
                "Get a free key at https://aistudio.google.com/apikey and add it to .env"
            )
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as exc:
            raise ImportError(
                "langchain-google-genai is not installed. "
                "Run: uv add langchain-google-genai"
            ) from exc
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0,
        )

    if p == "claude":
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set."
            )
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as exc:
            raise ImportError(
                "langchain-anthropic is not installed. "
                "Run: uv add langchain-anthropic"
            ) from exc
        return ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=anthropic_key,
            temperature=0,
        )

    raise ValueError(
        f"Unknown LLM provider: {p!r}. Choose one of: ollama, gemini, claude"
    )

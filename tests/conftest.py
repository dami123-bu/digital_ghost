"""
conftest.py

Session-wide test configuration. Redirects ChromaDB to a temporary
directory so tests never touch the real data/chroma store.
"""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="session")
def isolate_chroma_dir(tmp_path_factory):
    """Point config.CHROMA_DIR at a fresh temp directory for the entire test session."""
    import config

    test_chroma_dir = tmp_path_factory.mktemp("chroma")
    config.CHROMA_DIR = test_chroma_dir
    yield test_chroma_dir

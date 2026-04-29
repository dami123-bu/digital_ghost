"""
api/schemas.py — Pydantic models for the FastAPI backend.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class ToolCallRecord(BaseModel):
    name: str
    input: dict
    output: str


class QueryResponse(BaseModel):
    answer: str
    session_id: str
    mode: str
    provider: str = "ollama"             # which LLM backend answered
    tool_calls: list[ToolCallRecord] = []
    retrieved_docs: list[dict] = []      # each doc: {id, text, metadata, distance}
    injection_detected: bool = False     # True if defended mode stripped something
    turn_count: int = 1                  # number of human turns in the agent's thread


class IngestResponse(BaseModel):
    filename: str
    chunks_stored: int
    collection: str
    mode: str
    doc_id_prefix: str


class ModeRequest(BaseModel):
    mode: Literal["clean", "poisoned", "defended", "mcp_poisoned"]


class ModeResponse(BaseModel):
    mode: str
    mcp_pid: int | None = None


class AttackLogEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    event: str
    mode: str
    detail: str


class ProviderInfo(BaseModel):
    id: str
    label: str
    available: bool
    model: str


class ProviderRequest(BaseModel):
    provider: Literal["ollama", "gemini", "claude"]


class ProviderResponse(BaseModel):
    provider: str
    label: str


class HealthResponse(BaseModel):
    status: str
    mode: str
    provider: str = "ollama"
    mcp_running: bool
    chroma_clean_count: int = 0
    chroma_poisoned_count: int = 0

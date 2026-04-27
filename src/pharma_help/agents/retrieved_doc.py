from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievedDoc:
    id: str
    title: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    history: list[dict[str, str]] = field(default_factory=list)
    retrieved_docs: list[list[Any]] = field(default_factory=list)
    memory: list[str] = field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.history.append({"role": "assistant", "content": content})

    def add_retrieved_docs(self, docs: list[Any]) -> None:
        self.retrieved_docs.append(docs)

    def add_memory(self, note: str) -> None:
        self.memory.append(note)

    def recent_history(self, n: int = 6) -> list[dict[str, str]]:
        return self.history[-n:]
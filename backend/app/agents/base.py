from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    role: str
    output: dict[str, Any]
    confidence: float


@dataclass
class SharedMemory:
    facts: dict[str, Any] = field(default_factory=dict)
    decisions: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


class BaseAgent:
    role = "base"

    async def run(self, task: dict, memory: SharedMemory) -> AgentResult:
        raise NotImplementedError

from backend.app.agents.base import SharedMemory
from backend.app.agents.critic import CriticAgent
from backend.app.agents.fact_checker import FactCheckerAgent
from backend.app.agents.generator import GeneratorAgent
from backend.app.agents.planner import PlannerAgent
from backend.app.agents.reflection import ReflectionAgent


class AgentOrchestrator:
    def __init__(self):
        self.agents = [PlannerAgent(), GeneratorAgent(), CriticAgent(), FactCheckerAgent(), ReflectionAgent()]

    async def run(self, task: dict) -> dict:
        memory = SharedMemory()
        results = []
        for agent in self.agents:
            result = await agent.run(task, memory)
            results.append({"role": result.role, "output": result.output, "confidence": result.confidence})
        return {
            "results": results,
            "shared_memory": {"facts": memory.facts, "decisions": memory.decisions, "conflicts": memory.conflicts},
            "conflict_resolution": "blocked" if memory.conflicts else "approved_for_draft",
            "confidence": round(sum(r["confidence"] for r in results) / len(results), 4),
        }

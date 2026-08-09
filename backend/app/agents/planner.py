from backend.app.agents.base import AgentResult, BaseAgent, SharedMemory


class PlannerAgent(BaseAgent):
    role = "planner"

    async def run(self, task: dict, memory: SharedMemory) -> AgentResult:
        plan = ["ingest lore", "retrieve context", "generate draft", "critic review", "fact check", "reflection"]
        memory.decisions.extend(plan)
        return AgentResult(self.role, {"plan": plan}, 0.9)

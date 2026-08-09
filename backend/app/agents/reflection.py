from backend.app.agents.base import AgentResult, BaseAgent, SharedMemory


class ReflectionAgent(BaseAgent):
    role = "reflection"

    async def run(self, task: dict, memory: SharedMemory) -> AgentResult:
        return AgentResult(self.role, {"ready_for_user_review": not memory.conflicts}, 0.84)

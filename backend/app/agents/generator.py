from backend.app.agents.base import AgentResult, BaseAgent, SharedMemory


class GeneratorAgent(BaseAgent):
    role = "generator"

    async def run(self, task: dict, memory: SharedMemory) -> AgentResult:
        payload = {"generated": task, "constraints": memory.decisions}
        memory.facts["generated"] = payload
        return AgentResult(self.role, payload, 0.78)

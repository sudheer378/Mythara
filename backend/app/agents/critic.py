from backend.app.agents.base import AgentResult, BaseAgent, SharedMemory


class CriticAgent(BaseAgent):
    role = "critic"

    async def run(self, task: dict, memory: SharedMemory) -> AgentResult:
        issues = [] if task else ["empty task"]
        memory.conflicts.extend(issues)
        return AgentResult(self.role, {"issues": issues}, 0.82)

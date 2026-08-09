from backend.app.agents.base import AgentResult, BaseAgent, SharedMemory
from backend.app.ai.canon import CanonGuardian


class FactCheckerAgent(BaseAgent):
    role = "fact_checker"

    async def run(self, task: dict, memory: SharedMemory) -> AgentResult:
        report = CanonGuardian().validate(str(task))
        if not report["passed"]:
            memory.conflicts.append("canon_guardian_block")
        return AgentResult(self.role, report, report["confidence"])

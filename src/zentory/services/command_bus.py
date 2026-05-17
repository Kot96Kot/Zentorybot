from typing import Any

from zentory.agents.orchestrator import Orchestrator
from zentory.decision.engine import DecisionResult


class CommandBus:
    def __init__(self, orchestrator: Orchestrator) -> None:
        self.orchestrator = orchestrator

    async def dispatch(self, event: dict[str, Any]) -> DecisionResult:
        return await self.orchestrator.handle_event(event)

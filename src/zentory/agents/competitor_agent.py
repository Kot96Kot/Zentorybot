from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel


class CompetitorAgent(BaseAgent):
    name = "competitor"
    description = "Анализ конкурентов"
    supported_events = ("competitor",)

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ для процесса: Анализ конкурентов.",
            "event_type": str(event.get("event_type", "unknown")),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        return [
            Action(
                action_type="competitor_watch",
                title="Проверить mock-изменения конкурентов",
                description="Mock-рекомендация агента CompetitorAgent. Реальных API-вызовов нет.",
                payload={"mock": True, "agent": self.name, "source_event": event},
                risk_level=RiskLevel.LOW,
            )
        ]

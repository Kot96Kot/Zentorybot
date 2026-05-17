from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel


class CategoryAgent(BaseAgent):
    name = "category"
    description = "Новые продукты и категорийка"
    supported_events = ("category",)

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ для процесса: Новые продукты и категорийка.",
            "event_type": str(event.get("event_type", "unknown")),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        return [
            Action(
                action_type="category_opportunity",
                title="Найти mock-возможность в категории",
                description="Mock-рекомендация агента CategoryAgent. Реальных API-вызовов нет.",
                payload={"mock": True, "agent": self.name, "source_event": event},
                risk_level=RiskLevel.LOW,
            )
        ]

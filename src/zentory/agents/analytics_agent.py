from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel


class AnalyticsAgent(BaseAgent):
    name = "analytics"
    description = "Аналитика площадки и тренды"
    supported_events = ("analytics", "daily", "daily_digest", "alerts")

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ для процесса: Аналитика площадки и тренды.",
            "event_type": str(event.get("event_type", "unknown")),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        return [
            Action(
                action_type="daily_digest",
                title="Собрать mock-аналитику дня",
                description="Mock-рекомендация агента AnalyticsAgent. Реальных API-вызовов нет.",
                payload={"mock": True, "agent": self.name, "source_event": event},
                risk_level=RiskLevel.LOW,
            )
        ]

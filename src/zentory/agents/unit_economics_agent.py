from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel


class UnitEconomicsAgent(BaseAgent):
    name = "unit_economics"
    description = "Юнит-экономика и ценообразование"
    supported_events = ("unit_economics", "unit")

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ для процесса: Юнит-экономика и ценообразование.",
            "event_type": str(event.get("event_type", "unknown")),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        return [
            Action(
                action_type="price_guard",
                title="Проверить mock-маржинальность цены",
                description=(
                    "Mock-рекомендация агента UnitEconomicsAgent. Реальных API-вызовов нет."
                ),
                payload={"mock": True, "agent": self.name, "source_event": event},
                risk_level=RiskLevel.LOW,
            )
        ]

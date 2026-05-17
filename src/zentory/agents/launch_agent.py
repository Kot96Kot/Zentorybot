from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel


class LaunchAgent(BaseAgent):
    name = "launch"
    description = "Запуск новинок"
    supported_events = ("launch",)

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ для процесса: Запуск новинок.",
            "event_type": str(event.get("event_type", "unknown")),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        return [
            Action(
                action_type="launch_checklist",
                title="Создать mock-чеклист запуска новинки",
                description="Mock-рекомендация агента LaunchAgent. Реальных API-вызовов нет.",
                payload={"mock": True, "agent": self.name, "source_event": event},
                risk_level=RiskLevel.LOW,
            )
        ]

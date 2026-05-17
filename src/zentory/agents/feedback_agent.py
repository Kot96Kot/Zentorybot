from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel


class FeedbackAgent(BaseAgent):
    name = "feedback"
    description = "Отзывы и вопросы покупателей"
    supported_events = ("feedback",)

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ для процесса: Отзывы и вопросы покупателей.",
            "event_type": str(event.get("event_type", "unknown")),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        return [
            Action(
                action_type="feedback_reply_draft",
                title="Подготовить mock-черновик ответа",
                description="Mock-рекомендация агента FeedbackAgent. Реальных API-вызовов нет.",
                payload={"mock": True, "agent": self.name, "source_event": event},
                risk_level=RiskLevel.LOW,
            )
        ]

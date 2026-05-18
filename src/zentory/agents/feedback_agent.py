from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import ApprovalMode, RiskLevel


class FeedbackAgent(BaseAgent):
    name = "feedback"
    description = "Отзывы и вопросы покупателей"
    supported_events = ("feedback",)
    _HIGH_RISK_TAGS = {"complaint", "warranty", "return", "legal"}

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ для процесса: Отзывы и вопросы покупателей.",
            "event_type": str(event.get("event_type", "unknown")),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        rating = self._rating(payload)
        risk_tags = {
            str(tag).lower() for tag in payload.get("risk_tags", []) if tag is not None
        }
        high_risk = bool(risk_tags & self._HIGH_RISK_TAGS)
        negative_review = str(payload.get("kind", "")).lower() == "review" and rating <= 2
        knowledge_base = payload.get("knowledge_base", {})
        grounded_answer = self._grounded_answer(payload, knowledge_base)

        approval_mode = ApprovalMode.NONE
        risk_level = RiskLevel.LOW
        approval_reason = "standard_draft"
        if high_risk:
            approval_mode = ApprovalMode.HARD_APPROVAL
            risk_level = RiskLevel.HIGH
            approval_reason = "high_risk_feedback"
        elif negative_review:
            approval_mode = ApprovalMode.SOFT_APPROVAL
            risk_level = RiskLevel.MEDIUM
            approval_reason = "negative_review"

        return [
            Action(
                action_type="feedback_reply_draft",
                title="Подготовить mock-черновик ответа",
                description=self._description(approval_reason),
                payload={
                    "mock": True,
                    "agent": self.name,
                    "source_event": event,
                    "approval_reason": approval_reason,
                    "grounded_in_knowledge_base": grounded_answer is not None,
                    "knowledge_base_answer": grounded_answer,
                    "reply_text": self._reply_text(grounded_answer),
                },
                risk_level=risk_level,
                approval_mode=approval_mode,
            )
        ]

    @staticmethod
    def _rating(payload: dict[str, Any]) -> int:
        try:
            return int(payload.get("rating", 5))
        except (TypeError, ValueError):
            return 5

    @staticmethod
    def _grounded_answer(payload: dict[str, Any], knowledge_base: Any) -> str | None:
        if not isinstance(knowledge_base, dict) or not knowledge_base:
            return None
        text = str(payload.get("text", "")).lower()
        aliases = {
            "warranty": ("warranty", "гарант", "гарантия", "гарантий"),
            "return": ("return", "возврат", "вернуть"),
        }
        for key, value in knowledge_base.items():
            key_text = str(key).lower()
            markers = aliases.get(key_text, (key_text,))
            if any(marker in text for marker in markers):
                return str(value)
        return None

    @staticmethod
    def _reply_text(grounded_answer: str | None) -> str:
        if grounded_answer is None:
            return "Спасибо за обращение. Передадим вопрос менеджеру для проверки."
        return f"Спасибо за вопрос. По базе знаний: {grounded_answer}."

    @staticmethod
    def _description(approval_reason: str) -> str:
        if approval_reason == "high_risk_feedback":
            return "Mock-черновик ответа на рискованный отзыв. Требуется hard approval."
        if approval_reason == "negative_review":
            return "Mock-черновик ответа на негативный отзыв. Требуется approval."
        return "Mock-рекомендация агента FeedbackAgent. Реальных API-вызовов нет."

from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.content import ContentBrief, ContentCardDraft
from zentory.services.content_generation_service import ContentGenerationService


class ContentAgent(BaseAgent):
    name = "content"
    description = "Генерация draft-контента карточек товаров"
    supported_events = (
        "content",
        "content_new",
        "content_sku",
        "content_brief",
        "/content_new",
        "/content_sku",
        "/content_brief",
    )

    def __init__(self, service: ContentGenerationService | None = None) -> None:
        self.service = service or ContentGenerationService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        brief = self._brief_from_event(event)
        draft = await self.service.generate_draft(brief)
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock LLM draft карточки товара. Автопубликации нет.",
            "event_type": str(event.get("event_type", "unknown")),
            "draft": draft.model_dump(mode="json"),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        brief = self._brief_from_event(event)
        draft = await self.service.generate_draft(brief)
        return self._actions_for_draft(draft)

    def _brief_from_event(self, event: dict[str, Any]) -> ContentBrief:
        payload = event.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        sku = payload.get("sku")
        return self.service.build_mock_brief(sku=sku, payload=payload)

    def _actions_for_draft(self, draft: ContentCardDraft) -> list[Action]:
        draft_payload = draft.model_dump(mode="json")
        return [
            Action(
                action_type="content_card_draft_created",
                title=f"Draft карточки: {draft.seo_title}",
                description=(
                    "Mock LLM сгенерировал draft карточки товара. "
                    "Контент не публикуется автоматически."
                ),
                payload={"mock": True, "agent": self.name, "draft": draft_payload},
                risk_level=RiskLevel.MEDIUM,
            ),
            Action(
                action_type="content_apply_requires_approval",
                title=f"Approval перед применением контента: {draft.article}",
                description=(
                    "Перед любым применением контента нужен approval менеджера. "
                    "Safe mode запрещает автопубликацию."
                ),
                payload={
                    "mock": True,
                    "agent": self.name,
                    "draft": draft_payload,
                    "requires_approval": True,
                    "draft_mode": True,
                },
                risk_level=RiskLevel.HIGH,
            ),
        ]

from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.services.content_ctr_service import ContentCTRService


class ContentCTRAgent(BaseAgent):
    name = "content_ctr"
    description = "Content CTR Factory: гипотезы главного фото, prompts и CTR test plan"
    supported_events = (
        "content_sku",
        "content_brief",
        "content_hypotheses",
        "content_prompts",
        "ctr_test",
    )

    def __init__(self, service: ContentCTRService | None = None) -> None:
        self.service = service or ContentCTRService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        result = self._result_for_event(event)
        return {"agent": self.name, "content_ctr": result.model_dump(mode="json"), "mock": True}

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        result = self._result_for_event(event)
        card = {
            "status": f"Content CTR Factory для {result.brief.sku} готов",
            "problem": (
                f"current CTR {result.brief.current_ctr}% "
                f"ниже target {result.brief.target_ctr}%"
            ),
            "reason": "собраны боли, фичи, competitor references и mock CTR benchmark",
            "recommendation": (
                f"создать draft главного фото: {result.hypotheses[0].idea}; "
                "запустить CTR test без автопубликации"
            ),
            "risk": "MEDIUM",
            "approval_required": (
                "да: публикация требует approval; bulk update требует hard approval"
            ),
            "draft_only": True,
            "hypotheses_count": len(result.hypotheses),
            "ctr_test_plan": result.ctr_test_plan.model_dump(mode="json"),
        }
        return [
            Action(
                agent_name=self.name,
                action_type="content_ctr_factory_draft",
                title=f"Content CTR hypotheses: {result.brief.sku}",
                description="Mock draft гипотез и prompts для главного фото. Автопубликации нет.",
                payload={
                    "mock": True,
                    "source_event": event,
                    "content_ctr": result.model_dump(mode="json"),
                    "telegram_response": card,
                    "draft_only": True,
                },
                risk_level=RiskLevel.MEDIUM,
                approval_mode=ApprovalMode.SOFT_APPROVAL,
                rollback_available=False,
            ),
            Action(
                agent_name=self.name,
                action_type="content_bulk_update_requires_hard_approval",
                title="Hard approval для массовых изменений контента",
                description="Любая массовая публикация контента запрещена без hard approval.",
                payload={"mock": True, "sku": result.brief.sku, "draft_only": True},
                risk_level=RiskLevel.HIGH,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                rollback_available=False,
            ),
        ]

    def _result_for_event(self, event: dict[str, Any]):
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        sku = payload.get("sku")
        if sku and not payload.get("product_name"):
            return self.service.build_for_sku(str(sku))
        brief = self.service.build_brief(payload)
        hypotheses = self.service.generate_hypotheses(brief)
        prompts = self.service.generate_prompts(brief, hypotheses[:3])
        result = self.service.build_for_sku(brief.sku)
        return result.model_copy(
            update={
                "brief": brief,
                "hypotheses": hypotheses,
                "prompts": prompts,
                "ctr_test_plan": self.service.build_test_plan(brief),
            }
        )

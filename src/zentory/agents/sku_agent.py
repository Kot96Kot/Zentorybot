from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.services.sku_intelligence_service import SKUIntelligenceService


class SKUAgent(BaseAgent):
    name = "sku_intelligence"
    description = "Единая карточка анализа SKU"
    supported_events = ("sku_overview", "sku_intelligence", "sku")

    def __init__(self, service: SKUIntelligenceService | None = None) -> None:
        self.service = service or SKUIntelligenceService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        sku = str(payload.get("sku", "WB-MOCK-1"))
        card = self.service.build_card(sku)
        return card.model_dump(mode="json")

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        sku = str(payload.get("sku", "WB-MOCK-1"))
        card = self.service.build_card(sku)
        manager_card = self.service.to_manager_card(card)
        return [
            Action(
                agent_name=self.name,
                action_type="sku_intelligence_card",
                title=f"SKU Intelligence Card: {card.sku}",
                description="Mock карточка SKU: продажи, остатки, реклама, отзывы и рекомендации.",
                payload={
                    "mock": True,
                    "source_event": event,
                    "sku_intelligence": card.model_dump(mode="json"),
                    "telegram_response": manager_card,
                },
                risk_level=RiskLevel.HIGH if card.risks else RiskLevel.LOW,
                approval_mode=ApprovalMode.HARD_APPROVAL if card.risks else ApprovalMode.NONE,
                rollback_available=False,
                explanation=(
                    "SKU собран из mock-срезов продаж, остатков, рекламы, "
                    "отзывов и конкурентов."
                ),
                evidence=[
                    {"source": "sales", "label": "week_units", "value": card.sales.sales_qty_7d},
                    {
                        "source": "stock",
                        "label": "coverage_days",
                        "value": card.stock.days_of_coverage,
                    },
                    {
                        "source": "ads",
                        "label": "drr_percent",
                        "value": card.advertising.drr,
                    },
                    {"source": "reviews", "label": "rating", "value": card.reputation.rating},
                ],
            )
        ]

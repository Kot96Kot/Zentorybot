from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.schemas.supply import SupplyPriority, SupplyRecommendation
from zentory.services.supply_planner_service import SupplyPlannerService


class SupplyAgent(BaseAgent):
    name = "supply"
    description = "Supply & Localization Planner для отгрузок, подсортов и складских рисков"
    supported_events = ("stock_risks", "replenishment", "warehouses", "supply", "supply_sku")

    def __init__(self, service: SupplyPlannerService | None = None) -> None:
        self.service = service or SupplyPlannerService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        sku = self._sku_from_event(event)
        report = self.service.plan(sku=sku)
        return {"agent": self.name, "supply": report.model_dump(mode="json"), "mock": True}

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        event_type = str(event.get("event_type", "stock_risks"))
        sku = self._sku_from_event(event)
        report = self.service.plan(sku=sku)
        if event_type == "warehouses":
            card = {
                "status": "локализация складов рассчитана",
                "problem": f"складов с перераспределением: {self._redistribution_count(report)}",
                "reason": "сравнили регион, warehouse, localization_index и logistics_cost",
                "recommendation": "перенести запас на целевой склад при низкой локализации",
                "risk": "MEDIUM" if self._redistribution_count(report) else "LOW",
                "warehouses": [item.model_dump(mode="json") for item in report.warehouses],
            }
            return [self._action("warehouses", "Supply localization plan", event, card)]
        if event_type == "replenishment":
            recommendations = report.replenishment
            card = self._manager_card(
                status="план отгрузок и подсортов готов",
                recommendations=recommendations,
                extra={"ads_alerts": report.ads_alerts},
            )
            return [self._action("replenishment", "Supply replenishment plan", event, card)]
        recommendations = report.risks or report.recommendations
        card = self._manager_card(
            status="риски остатков по складам рассчитаны",
            recommendations=recommendations,
            extra={"ads_alerts": report.ads_alerts},
        )
        return [self._action("stock_risks", "Supply stock risks", event, card)]

    @staticmethod
    def _manager_card(
        *, status: str, recommendations: list[SupplyRecommendation], extra: dict[str, Any]
    ) -> dict[str, Any]:
        critical = [item for item in recommendations if item.priority == SupplyPriority.CRITICAL]
        high = [item for item in recommendations if item.priority == SupplyPriority.HIGH]
        top = recommendations[0] if recommendations else None
        return {
            "status": status,
            "problem": f"critical={len(critical)}, high={len(high)}, total={len(recommendations)}",
            "reason": top.reason if top else "mock supply data без критичных отклонений",
            "recommendation": (
                f"{top.sku}: отгрузить {top.recommended_supply_qty} на {top.target_warehouse}"
                if top
                else "наблюдать"
            ),
            "risk": "HIGH" if critical else "MEDIUM" if high else "LOW",
            "recommendations": [item.model_dump(mode="json") for item in recommendations],
            **extra,
        }

    @staticmethod
    def _action(
        action_type: str, title: str, event: dict[str, Any], card: dict[str, Any]
    ) -> Action:
        risk = card.get("risk", "LOW")
        risk_level = (
            RiskLevel.HIGH
            if risk == "HIGH"
            else RiskLevel.MEDIUM
            if risk == "MEDIUM"
            else RiskLevel.LOW
        )
        return Action(
            agent_name="supply",
            action_type=action_type,
            title=title,
            description="Mock-only Supply & Localization Planner. Реальных API-вызовов нет.",
            payload={"mock": True, "source_event": event, "telegram_response": card},
            risk_level=risk_level,
            approval_mode=(
                ApprovalMode.HARD_APPROVAL
                if risk_level == RiskLevel.HIGH
                else ApprovalMode.NONE
            ),
            rollback_available=False,
        )

    @staticmethod
    def _sku_from_event(event: dict[str, Any]) -> str | None:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        raw = payload.get("sku")
        return str(raw) if raw else None

    @staticmethod
    def _redistribution_count(report: Any) -> int:
        return sum(1 for item in report.warehouses if item.redistribution_recommended)

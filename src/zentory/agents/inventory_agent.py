from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.inventory import InventoryPriority, InventorySkuReport, InventorySummary
from zentory.services.inventory_service import InventoryService


class InventoryAgent(BaseAgent):
    name = "inventory"
    description = "Отгрузки, подсорты, остатки и риски out-of-stock"
    supported_events = (
        "inventory",
        "stocks",
        "stock_risks",
        "replenishment",
        "sku_stock",
        "/stocks",
        "/stock_risks",
        "/replenishment",
        "/sku_stock",
    )

    def __init__(self, service: InventoryService | None = None) -> None:
        self.service = service or InventoryService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        summary = self._summary_for_event(event)
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ остатков, подсортов и отгрузок. Реальные API не вызываются.",
            "event_type": str(event.get("event_type", "unknown")),
            "inventory": summary.model_dump(mode="json"),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        summary = self._summary_for_event(event)
        actions: list[Action] = []
        for report in self._reports_for_event_type(event, summary):
            actions.append(self._report_action(report))
            for recommendation in report.recommendations:
                actions.append(
                    Action(
                        action_type=f"inventory_{recommendation.recommendation_type}_recommendation",
                        title=f"{recommendation.title}: {report.sku}",
                        description=recommendation.description,
                        payload={
                            "mock": True,
                            "agent": self.name,
                            "recommendation_only": True,
                            "report": report.model_dump(mode="json"),
                            "recommendation": recommendation.model_dump(mode="json"),
                        },
                        risk_level=self._risk_for_priority(recommendation.priority),
                    )
                )
            for alert in report.alerts_for_ads_agent:
                actions.append(
                    Action(
                        action_type="inventory_ads_alert",
                        title=f"Alert в AdsAgent: {report.sku}",
                        description=alert,
                        payload={
                            "mock": True,
                            "agent": self.name,
                            "report": report.model_dump(mode="json"),
                        },
                        risk_level=RiskLevel.HIGH,
                    )
                )
        return actions

    def _summary_for_event(self, event: dict[str, Any]) -> InventorySummary:
        payload = event.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        return self.service.analyze(sku=payload.get("sku"))

    @staticmethod
    def _reports_for_event_type(
        event: dict[str, Any], summary: InventorySummary
    ) -> list[InventorySkuReport]:
        event_type = str(event.get("event_type", ""))
        if event_type == "stock_risks":
            return summary.out_of_stock_risks
        if event_type == "replenishment":
            return [report for report in summary.reports if report.recommendations]
        return summary.reports

    def _report_action(self, report: InventorySkuReport) -> Action:
        return Action(
            action_type="inventory_stock_report",
            title=f"Остатки {report.sku}: {report.status}",
            description="Mock-отчет по остаткам, покрытию и рекомендациям по подсорту/отгрузке.",
            payload={"mock": True, "agent": self.name, "report": report.model_dump(mode="json")},
            risk_level=self._risk_for_priority(report.priority),
        )

    @staticmethod
    def _risk_for_priority(priority: InventoryPriority) -> RiskLevel:
        if priority == InventoryPriority.CRITICAL:
            return RiskLevel.HIGH
        if priority == InventoryPriority.HIGH:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

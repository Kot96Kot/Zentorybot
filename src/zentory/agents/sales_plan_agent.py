from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.sales_plan import SalesPlanReport
from zentory.services.sales_plan_service import SalesPlanService


class SalesPlanAgent(BaseAgent):
    name = "sales_plan"
    description = "План продаж по SKU на день, неделю и месяц"
    supported_events = ("sales_plan", "sales_plan_sku", "/sales_plan", "/sales_plan_sku")

    def __init__(self, service: SalesPlanService | None = None) -> None:
        self.service = service or SalesPlanService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        reports = self._reports_for_event(event)
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ плана продаж по SKU.",
            "event_type": str(event.get("event_type", "unknown")),
            "reports": [report.model_dump(mode="json") for report in reports],
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        reports = self._reports_for_event(event)
        actions: list[Action] = []
        for report in reports:
            actions.extend(self._actions_for_report(report))
        if not actions:
            actions.append(
                Action(
                    action_type="sales_plan_status_ok",
                    title="План продаж выполняется",
                    description="Mock-рекомендация: продолжать мониторинг плана продаж.",
                    payload={"mock": True, "agent": self.name, "reports": []},
                    risk_level=RiskLevel.LOW,
                )
            )
        return actions

    def _reports_for_event(self, event: dict[str, Any]) -> list[SalesPlanReport]:
        payload = event.get("payload", {})
        sku = payload.get("sku") if isinstance(payload, dict) else None
        return self.service.calculate_reports(sku=sku)

    def _actions_for_report(self, report: SalesPlanReport) -> list[Action]:
        actions: list[Action] = [
            Action(
                action_type="sales_plan_report",
                title=f"План продаж для {report.sku}: {report.status}",
                description="Mock-отчет с планом продаж на день, неделю и месяц.",
                payload={
                    "mock": True,
                    "agent": self.name,
                    "report": report.model_dump(mode="json"),
                },
                risk_level=RiskLevel.LOW,
            )
        ]
        for alert in report.alerts:
            actions.append(
                Action(
                    action_type="sales_plan_alert",
                    title=f"Алерт по плану продаж: {report.sku}",
                    description=alert,
                    payload={
                        "mock": True,
                        "agent": self.name,
                        "report": report.model_dump(mode="json"),
                    },
                    risk_level=RiskLevel.MEDIUM,
                )
            )
        for task in report.tasks:
            actions.append(
                Action(
                    action_type="content_analysis_task",
                    title=f"Задача на анализ карточки: {report.sku}",
                    description=task,
                    payload={
                        "mock": True,
                        "agent": self.name,
                        "report": report.model_dump(mode="json"),
                    },
                    risk_level=RiskLevel.MEDIUM,
                )
            )
        return actions

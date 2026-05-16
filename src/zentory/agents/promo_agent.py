from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.promo import PromoAnalysisReport, PromoSummary
from zentory.services.promo_analysis_service import PromoAnalysisService


class PromoAgent(BaseAgent):
    name = "promo"
    description = "Анализ акций, маржи и рисков участия"
    supported_events = (
        "promo",
        "promo_check",
        "promo_sku",
        "promo_list",
        "/promo_check",
        "/promo_sku",
        "/promo_list",
    )

    def __init__(self, service: PromoAnalysisService | None = None) -> None:
        self.service = service or PromoAnalysisService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        summary = self._summary_for_event(event)
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ акций. Все действия требуют approval.",
            "event_type": str(event.get("event_type", "unknown")),
            "promo": summary.model_dump(mode="json"),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        summary = self._summary_for_event(event)
        reports = (
            summary.dangerous_skus
            if str(event.get("event_type")) == "promo_list"
            else summary.reports
        )
        actions: list[Action] = []
        for report in reports:
            actions.append(self._report_action(report))
            actions.append(self._approval_action(report))
        return actions

    def _summary_for_event(self, event: dict[str, Any]) -> PromoSummary:
        payload = event.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        return self.service.analyze(sku=payload.get("sku"))

    @staticmethod
    def _report_action(report: PromoAnalysisReport) -> Action:
        return Action(
            action_type="promo_analysis_report",
            title=f"Анализ акции {report.sku}: {report.recommendation.decision}",
            description="Mock-отчет по акции, марже и прогнозу прибыли.",
            payload={
                "mock": True,
                "agent": "promo",
                "requires_approval": True,
                "report": report.model_dump(mode="json"),
            },
            risk_level=RiskLevel.MEDIUM,
        )

    @staticmethod
    def _approval_action(report: PromoAnalysisReport) -> Action:
        return Action(
            action_type="promo_requires_approval",
            title=f"Approval по акции: {report.sku}",
            description=report.recommendation.description,
            payload={
                "mock": True,
                "agent": "promo",
                "requires_approval": True,
                "recommendation_only": True,
                "report": report.model_dump(mode="json"),
                "recommendation": report.recommendation.model_dump(mode="json"),
            },
            risk_level=report.risk_level,
        )

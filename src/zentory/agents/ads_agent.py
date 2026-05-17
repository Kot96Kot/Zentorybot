from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.ads import AdsCampaignReport, AdsRecommendationType
from zentory.services.ads_analysis_service import AdsAnalysisService


class AdsAgent(BaseAgent):
    name = "ads"
    description = "Внутренняя реклама, ДРР, CTR и рекомендации по ставкам"
    supported_events = (
        "ads",
        "ads_today",
        "ads_sku",
        "ads_campaign",
        "ads_alerts",
        "/ads_today",
        "/ads_sku",
        "/ads_campaign",
        "/ads_alerts",
    )

    def __init__(self, service: AdsAnalysisService | None = None) -> None:
        self.service = service or AdsAnalysisService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        reports = self._reports_for_event(event)
        return {
            "agent": self.name,
            "mock": True,
            "summary": "Mock-анализ внутренних рекламных кампаний. Реальные ставки не меняются.",
            "event_type": str(event.get("event_type", "unknown")),
            "reports": [report.model_dump(mode="json") for report in reports],
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        reports = self._reports_for_event(event)
        actions: list[Action] = []
        for report in reports:
            actions.append(self._report_action(report))
            for recommendation in report.recommendations:
                actions.append(
                    Action(
                        action_type=f"ads_recommendation_{recommendation.recommendation_type}",
                        title=recommendation.title,
                        description=(
                            f"Recommendation only: {recommendation.description} "
                            "Реальные изменения ставок не выполняются."
                        ),
                        payload={
                            "mock": True,
                            "agent": self.name,
                            "recommendation_only": True,
                            "requires_approval": recommendation.requires_approval,
                            "report": report.model_dump(mode="json"),
                            "recommendation": recommendation.model_dump(mode="json"),
                        },
                        risk_level=self._risk_for_recommendation(
                            recommendation.recommendation_type
                        ),
                    )
                )
        return actions

    def _reports_for_event(self, event: dict[str, Any]) -> list[AdsCampaignReport]:
        payload = event.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        event_type = str(event.get("event_type", ""))
        sku = payload.get("sku")
        campaign_id = payload.get("campaign_id")
        if event_type == "ads_alerts":
            return [report for report in self.service.analyze_many() if report.alerts]
        return self.service.analyze_many(sku=sku, campaign_id=campaign_id)

    def _report_action(self, report: AdsCampaignReport) -> Action:
        return Action(
            action_type="ads_campaign_report",
            title=f"Отчет по рекламе {report.campaign_id}: {report.status}",
            description="Mock-отчет по рекламной кампании с рекомендациями без применения ставок.",
            payload={"mock": True, "agent": self.name, "report": report.model_dump(mode="json")},
            risk_level=RiskLevel.LOW,
        )

    @staticmethod
    def _risk_for_recommendation(recommendation_type: AdsRecommendationType) -> RiskLevel:
        if recommendation_type in {
            AdsRecommendationType.PAUSE_CAMPAIGN,
            AdsRecommendationType.CRITICAL_SPEND_ALERT,
            AdsRecommendationType.FORBID_ADS_SCALE,
        }:
            return RiskLevel.HIGH
        if recommendation_type == AdsRecommendationType.KEEP_MONITORING:
            return RiskLevel.LOW
        return RiskLevel.MEDIUM

import pytest

from zentory.agents.ads_agent import AdsAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.ads import AdsRecommendationType, AdsReportStatus
from zentory.services.ads_analysis_service import AdsAnalysisService


@pytest.mark.asyncio
async def test_ads_agent_returns_campaign_reports_for_today_command() -> None:
    agent = AdsAgent()

    analysis = await agent.analyze({"event_type": "ads_today", "payload": {"mock": True}})

    assert analysis["mock"] is True
    assert analysis["reports"]
    assert analysis["reports"][0]["impressions"] > 0
    assert "drr" in analysis["reports"][0]


@pytest.mark.asyncio
async def test_ads_agent_filters_by_campaign_and_creates_recommendation_actions() -> None:
    agent = AdsAgent()

    actions = await agent.propose_actions(
        {"event_type": "ads_campaign", "payload": {"campaign_id": "WB-ADS-101"}}
    )

    assert actions
    assert all(action.payload["report"]["campaign_id"] == "WB-ADS-101" for action in actions)
    assert any("pause_campaign" in action.action_type for action in actions)
    assert any(action.risk_level == RiskLevel.HIGH for action in actions)
    assert all(action.payload.get("mock") is True for action in actions)


def test_ads_analysis_service_detects_profitable_campaign_and_raise_bid() -> None:
    service = AdsAnalysisService()

    report = service.analyze_many(campaign_id="YM-ADS-303")[0]

    recommendation_types = {
        recommendation.recommendation_type for recommendation in report.recommendations
    }
    assert report.status == AdsReportStatus.WARNING
    assert AdsRecommendationType.RAISE_BID_CAREFULLY in recommendation_types


def test_ads_analysis_service_sends_critical_alert_for_high_spend_no_orders() -> None:
    service = AdsAnalysisService()

    report = service.analyze_many(campaign_id="WB-ADS-101")[0]

    recommendation_types = {
        recommendation.recommendation_type for recommendation in report.recommendations
    }
    assert report.status == AdsReportStatus.CRITICAL
    assert AdsRecommendationType.PAUSE_CAMPAIGN in recommendation_types
    assert AdsRecommendationType.CRITICAL_SPEND_ALERT in recommendation_types
    assert report.alerts

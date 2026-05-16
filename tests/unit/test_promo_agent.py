import pytest

from zentory.agents.promo_agent import PromoAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.promo import PromoDecision
from zentory.services.promo_analysis_service import PromoAnalysisService


@pytest.mark.asyncio
async def test_promo_agent_returns_promo_summary_for_check_command() -> None:
    agent = PromoAgent()

    analysis = await agent.analyze({"event_type": "promo_check", "payload": {"mock": True}})

    assert analysis["mock"] is True
    assert analysis["promo"]["reports"]
    assert analysis["promo"]["dangerous_skus"]


@pytest.mark.asyncio
async def test_promo_agent_filters_by_sku_and_requires_approval() -> None:
    agent = PromoAgent()

    actions = await agent.propose_actions(
        {"event_type": "promo_sku", "payload": {"sku": "ZNT-OZON-002"}}
    )

    assert actions
    assert all(action.payload["report"]["sku"] == "ZNT-OZON-002" for action in actions)
    assert any(action.action_type == "promo_requires_approval" for action in actions)
    assert all(action.payload["requires_approval"] is True for action in actions)
    assert any(action.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL} for action in actions)


def test_promo_analysis_rejects_below_mandatory_costs_as_critical() -> None:
    service = PromoAnalysisService()

    report = service.analyze(sku="ZNT-OZON-002").reports[0]

    assert report.can_participate is False
    assert report.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert report.recommendation.decision == PromoDecision.REJECT
    assert report.dangerous is True


def test_promo_analysis_allows_slow_mover_with_approval() -> None:
    service = PromoAnalysisService()

    report = service.analyze(sku="ZNT-YM-003").reports[0]

    assert report.can_participate is True
    assert report.recommendation.decision == PromoDecision.ALLOW_WITH_APPROVAL
    assert report.recommendation.requires_approval is True
    assert report.risk_level == RiskLevel.HIGH

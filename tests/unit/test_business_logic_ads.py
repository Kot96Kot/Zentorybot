from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.safety_engine import SafetyEngine
from zentory.schemas.ads import AdsCampaignMetrics, AdsRecommendationType, AdsReportStatus
from zentory.services.ads_analysis_service import AdsAnalysisService


def _campaign(**overrides: object) -> AdsCampaignMetrics:
    data = {
        "campaign_id": "ADS-AUDIT-1",
        "sku": "SKU-ADS-1",
        "marketplace": "wildberries",
        "campaign_name": "Audit campaign",
        "impressions": 10_000,
        "ctr": 0.03,
        "clicks": 300,
        "cpc": 20.0,
        "spend": 6_000.0,
        "orders": 10,
        "revenue": 50_000.0,
        "cart_conversion": 0.12,
        "order_conversion": 0.03,
        "average_position": 4.0,
        "bid": 50.0,
        "sku_stock": 100,
        "sku_margin": 0.35,
        "drr_limit": 0.18,
        "daily_spend_limit": 10_000.0,
    }
    data.update(overrides)
    return AdsCampaignMetrics(**data)


def test_bid_increase_is_blocked_when_stock_is_less_than_7_days() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="ad_bid_increase",
        title="Increase ad bid",
        description="Audit low-stock ad bid guard",
        payload={"current_bid": 100, "new_bid": 105, "stock_days": 6},
    )

    decision = engine.evaluate(action)

    assert decision.risk_level == RiskLevel.CRITICAL
    assert decision.approval_mode == ApprovalMode.HARD_APPROVAL
    assert decision.blocked is True
    assert decision.allowed_to_execute is False


def test_drr_above_limit_creates_warning_or_critical() -> None:
    report = AdsAnalysisService().analyze(_campaign(spend=15_000, orders=2, revenue=50_000))

    assert report.drr > report.sku_margin or report.drr > 0.18
    assert report.status in {AdsReportStatus.WARNING, AdsReportStatus.CRITICAL}
    assert report.recommendations


def test_spend_without_orders_proposes_pause_but_requires_approval() -> None:
    report = AdsAnalysisService().analyze(_campaign(spend=7_500, orders=0, revenue=0))

    pause = [
        item
        for item in report.recommendations
        if item.recommendation_type == AdsRecommendationType.PAUSE_CAMPAIGN
    ]
    assert pause
    assert pause[0].requires_approval is True
    assert pause[0].can_execute_automatically is False


def test_bid_increase_above_10_percent_requires_approval() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="ad_bid_increase",
        title="Increase ad bid",
        description="Audit bid-increase approval threshold",
        payload={"current_bid": 100, "new_bid": 111, "stock_days": 14},
    )

    decision = engine.evaluate(action)

    assert decision.approval_mode == ApprovalMode.SOFT_APPROVAL
    assert decision.requires_approval is True
    assert decision.allowed_to_execute is False

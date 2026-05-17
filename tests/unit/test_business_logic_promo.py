import pytest

from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.safety_engine import SafetyEngine
from zentory.schemas.promo import PromoDecision, PromoSkuInput
from zentory.services.promo_analysis_service import PromoAnalysisService


def _promo(**overrides: object) -> PromoSkuInput:
    data = {
        "sku": "SKU-PROMO-1",
        "current_price": 2_000.0,
        "promo_price": 1_700.0,
        "discount_percent": 0.15,
        "commission_percent": 0.18,
        "logistics_cost": 130.0,
        "cost_price": 800.0,
        "advertising_cost_per_unit": 120.0,
        "tax_percent": 0.06,
        "minimum_margin_percent": 0.18,
        "current_sales": 10,
        "stock": 300,
        "forecast_sales_growth_percent": 0.3,
        "promo_duration_days": 10,
        "storage_cost_per_unit": 10.0,
        "return_logistics_per_unit": 25.0,
    }
    data.update(overrides)
    return PromoSkuInput(**data)


def test_promo_below_minimum_margin_is_rejected() -> None:
    report = PromoAnalysisService().analyze_item(_promo(promo_price=1_450.0))

    assert report.can_participate is False
    assert report.recommendation.decision == PromoDecision.REJECT
    assert report.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert report.dangerous is True


def test_promo_below_cost_plus_expenses_is_critical() -> None:
    report = PromoAnalysisService().analyze_item(_promo(promo_price=900.0))

    assert report.risk_level == RiskLevel.CRITICAL
    assert report.recommendation.decision == PromoDecision.REJECT
    assert report.can_participate is False


def test_slow_mover_promo_requires_approval() -> None:
    report = PromoAnalysisService().analyze_item(
        _promo(promo_price=1_360.0, is_slow_mover=True, stock=800)
    )

    assert report.recommendation.decision == PromoDecision.ALLOW_WITH_APPROVAL
    assert report.recommendation.requires_approval is True
    assert report.risk_level == RiskLevel.HIGH


@pytest.mark.xfail(strict=True, reason="Promo safety does not inspect bulk SKU participation")
def test_mass_promo_participation_requires_hard_approval() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="promo_participation",
        title="Join promo for many SKUs",
        description="Bulk marketplace promo participation audit",
        payload={"margin_percent": 25, "sku_count": 200},
    )

    decision = engine.evaluate(action)

    assert decision.approval_mode == ApprovalMode.HARD_APPROVAL
    assert decision.requires_hard_approval is True
    assert decision.allowed_to_execute is False

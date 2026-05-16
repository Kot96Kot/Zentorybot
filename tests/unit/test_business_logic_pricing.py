import pytest

from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.safety_engine import SafetyEngine


def _evaluate_price(payload: dict[str, float]):
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="price_change",
        title="Change SKU price",
        description="Business-rule audit for marketplace price change",
        payload=payload,
    )
    return engine.evaluate(action)


def test_price_change_above_5_percent_requires_approval() -> None:
    decision = _evaluate_price({"current_price": 1_000, "new_price": 1_060})

    assert decision.approval_mode == ApprovalMode.SOFT_APPROVAL
    assert decision.requires_approval is True
    assert decision.allowed_to_execute is False


@pytest.mark.xfail(
    strict=True, reason="SafetyRules does not escalate >15% price changes to hard approval"
)
def test_price_change_above_15_percent_requires_hard_approval() -> None:
    decision = _evaluate_price({"current_price": 1_000, "new_price": 1_160})

    assert decision.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    assert decision.approval_mode == ApprovalMode.HARD_APPROVAL
    assert decision.requires_hard_approval is True
    assert decision.allowed_to_execute is False


@pytest.mark.xfail(strict=True, reason="Price guard ignores minimum margin payload")
def test_price_change_below_minimum_margin_is_blocked() -> None:
    decision = _evaluate_price(
        {
            "current_price": 1_000,
            "new_price": 930,
            "new_margin_percent": 0.09,
            "minimum_margin_percent": 0.15,
        }
    )

    assert decision.blocked is True
    assert decision.allowed_to_execute is False


@pytest.mark.xfail(strict=True, reason="Price guard ignores себестоимость + обязательные расходы")
def test_price_below_cost_plus_mandatory_expenses_is_critical() -> None:
    decision = _evaluate_price(
        {
            "current_price": 1_000,
            "new_price": 700,
            "cost_price": 600,
            "mandatory_expenses": 180,
        }
    )

    assert decision.risk_level == RiskLevel.CRITICAL
    assert decision.approval_mode == ApprovalMode.HARD_APPROVAL
    assert decision.blocked is True
    assert decision.allowed_to_execute is False

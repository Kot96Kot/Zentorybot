from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.safety_engine import SafetyEngine
from zentory.services.audit_service import AuditService


def test_price_change_3_percent_passes_as_low() -> None:
    audit = AuditService()
    engine = SafetyEngine(mode=AutomationMode.AUTO, audit_service=audit)
    action = Action(
        action_type="price_change",
        title="Change price",
        description="Mock safe price change",
        payload={"change_percent": 3},
    )

    decision = engine.evaluate(action)

    assert decision.risk_level == RiskLevel.LOW
    assert decision.approval_mode == ApprovalMode.NONE
    assert decision.allowed_to_execute is True
    assert decision.requires_approval is False


def test_price_change_12_percent_requires_approval() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="price_change",
        title="Change price",
        description="Mock risky price change",
        payload={"change_percent": 12},
    )

    decision = engine.evaluate(action)

    assert decision.risk_level == RiskLevel.MEDIUM
    assert decision.approval_mode == ApprovalMode.SOFT_APPROVAL
    assert decision.requires_approval is True
    assert decision.allowed_to_execute is False


def test_ad_bid_increase_20_percent_requires_approval() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="ad_bid_increase",
        title="Increase bid",
        description="Mock bid increase",
        payload={"increase_percent": 20, "stock_days": 14},
    )

    decision = engine.evaluate(action)

    assert decision.risk_level == RiskLevel.MEDIUM
    assert decision.requires_approval is True
    assert decision.allowed_to_execute is False


def test_promo_below_margin_gets_critical() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="promo_participation",
        title="Join promo",
        description="Mock promo",
        payload={"margin_percent": 10},
    )

    decision = engine.evaluate(action)

    assert decision.risk_level == RiskLevel.CRITICAL
    assert decision.approval_mode == ApprovalMode.HARD_APPROVAL
    assert decision.requires_hard_approval is True
    assert decision.blocked is True
    assert decision.allowed_to_execute is False


def test_shadow_mode_does_not_execute_action() -> None:
    engine = SafetyEngine(mode=AutomationMode.SHADOW)
    action = Action(
        action_type="price_change",
        title="Change price",
        description="Mock safe price change",
        payload={"change_percent": 3},
    )

    decision = engine.evaluate(action)

    assert decision.risk_level == RiskLevel.LOW
    assert decision.allowed_to_execute is False
    assert "shadow mode" in " ".join(decision.reasons)


def test_audit_log_created_for_each_proposed_action() -> None:
    audit = AuditService()
    engine = SafetyEngine(mode=AutomationMode.ASSISTANT, audit_service=audit)
    actions = [
        Action(
            action_type="price_change",
            title="Change price",
            description="Mock price action",
            payload={"change_percent": 3},
        ),
        Action(
            action_type="ad_bid_increase",
            title="Increase bid",
            description="Mock bid action",
            payload={"increase_percent": 5, "stock_days": 12},
        ),
    ]

    for action in actions:
        engine.evaluate(action)

    records = audit.list_records()
    safety_records = [
        record for record in records if record["event_type"] == "safety_action_evaluated"
    ]
    assert len(safety_records) == len(actions)
    assert {record["payload"]["action_id"] for record in safety_records} == {
        action.action_id for action in actions
    }

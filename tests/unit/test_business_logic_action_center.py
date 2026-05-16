import pytest

from zentory.actions.action_center import ActionCenter
from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel
from zentory.services.audit_service import AuditService


@pytest.mark.xfail(strict=True, reason="ActionCenter.execute_action is not idempotent yet")
def test_action_cannot_execute_twice() -> None:
    center = ActionCenter()
    action = center.create_action(
        agent_name="AdsAgent",
        action_type="ad_bid_change",
        title="Increase bid",
        description="Audit duplicate execution guard",
        approval_mode=ApprovalMode.NONE,
    )

    first = center.execute_action(action.action_id)
    second = center.execute_action(action.action_id)

    assert first.status == ActionStatus.EXECUTED
    assert second.payload.get("mock_execution_count", 1) == 1


def test_rejected_action_cannot_execute() -> None:
    center = ActionCenter()
    action = center.create_action(
        agent_name="PromoAgent",
        action_type="promo_participation",
        title="Reject promo",
        description="Rejected action audit",
        approval_mode=ApprovalMode.HARD_APPROVAL,
    )

    center.reject_action(action.action_id)
    executed = center.execute_action(action.action_id)

    assert executed.status == ActionStatus.REJECTED
    assert executed.payload.get("mock_execution") is None


def test_executed_action_rolls_back_only_when_rollback_is_available() -> None:
    center = ActionCenter()
    action = center.create_action(
        agent_name="ContentAgent",
        action_type="content_update",
        title="No rollback action",
        description="Rollback availability audit",
        rollback_available=False,
    )

    center.execute_action(action.action_id)
    rolled_back = center.rollback_action(action.action_id)

    assert rolled_back.status == ActionStatus.EXECUTED
    assert rolled_back.payload.get("mock_rollback") is None


def test_action_creation_has_audit_log() -> None:
    audit = AuditService()
    center = ActionCenter(audit_service=audit)

    action = center.create_action(
        agent_name="InventoryAgent",
        action_type="replenishment",
        title="Create supply task",
        description="Audit log coverage",
    )

    records = audit.list_records()
    assert any(
        record["event_type"] == "action_center_action_created"
        and record["payload"]["action_id"] == action.action_id
        for record in records
    )


@pytest.mark.xfail(
    strict=True, reason="ActionCenter trusts caller-provided approval_mode for HIGH/CRITICAL"
)
def test_high_and_critical_actions_cannot_execute_without_hard_approval() -> None:
    center = ActionCenter()
    action = center.create_action(
        agent_name="PricingAgent",
        action_type="price_change",
        title="Dangerous price change",
        description="HIGH risk action without hard approval must not execute",
        risk_level=RiskLevel.HIGH,
        approval_mode=ApprovalMode.NONE,
    )

    executed = center.execute_action(action.action_id)

    assert executed.status != ActionStatus.EXECUTED
    assert executed.payload.get("mock_execution") is None

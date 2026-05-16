from zentory.actions.action_center import ActionCenter
from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel
from zentory.services.audit_service import AuditService


def test_create_action_contains_required_fields() -> None:
    center = ActionCenter()

    action = center.create_action(
        agent_name="AdsAgent",
        action_type="ad_bid_increase",
        title="Increase bid for keyword",
        description="Raise bid to restore impressions",
        before_state={"bid": 100},
        after_state={"bid": 108},
        payload={"campaign_id": "ADS-7"},
        risk_level=RiskLevel.LOW,
        approval_mode=ApprovalMode.NONE,
        rollback_available=True,
        explanation="CTR is above target and stock is healthy",
        evidence=[{"source": "ads", "label": "ctr", "value": "3.1%"}],
    )

    assert action.action_id
    assert action.created_at is not None
    assert action.agent_name == "AdsAgent"
    assert action.before_state == {"bid": 100}
    assert action.after_state == {"bid": 108}
    assert action.status == ActionStatus.PROPOSED
    assert action.rollback_available is True
    assert action.evidence[0].label == "ctr"


def test_preview_action_shows_why_risk_data_changes_and_buttons() -> None:
    center = ActionCenter()
    action = center.create_action(
        agent_name="UnitEconomicsAgent",
        action_type="price_change",
        title="Reduce price by 3%",
        description="Price is above competitors",
        before_state={"price": 1000, "margin": 28},
        after_state={"price": 970, "margin": 25},
        risk_level=RiskLevel.LOW,
        approval_mode=ApprovalMode.NONE,
        explanation="Competitors are 2-4% cheaper",
        evidence=[{"source": "competitors", "label": "median_price", "value": 965}],
    )

    preview = center.preview_action(action.action_id)

    assert preview.action_id == action.action_id
    assert preview.reason == "Competitors are 2-4% cheaper"
    assert preview.risk_level == RiskLevel.LOW
    assert preview.data_used[0].source == "competitors"
    assert preview.changes["price"] == {"before": 1000, "after": 970}
    assert preview.buttons[0]["command"] == f"/approve {action.action_id}"
    assert preview.buttons[1]["command"] == f"/reject {action.action_id}"


def test_approve_execute_and_rollback_are_mock_only() -> None:
    audit = AuditService()
    center = ActionCenter(audit_service=audit)
    action = center.create_action(
        agent_name="PromoAgent",
        action_type="promo_participation",
        title="Join safe promo",
        description="Margin remains above threshold",
        before_state={"promo": None},
        after_state={"promo": "SPRING"},
        risk_level=RiskLevel.MEDIUM,
        approval_mode=ApprovalMode.SOFT_APPROVAL,
        rollback_available=True,
    )

    approved = center.approve_action(action.action_id, approved_by="owner")
    assert approved.status == ActionStatus.APPROVED

    executed = center.execute_action(action.action_id)
    assert executed.status == ActionStatus.EXECUTED

    rolled_back = center.rollback_action(action.action_id)
    assert rolled_back.status == ActionStatus.ROLLED_BACK
    assert rolled_back.payload["mock_execution"] is True
    assert rolled_back.payload["mock_rollback"] is True
    assert rolled_back.payload["external_api_called"] is False
    event_types = [record["event_type"] for record in audit.list_records()]
    assert "action_center_action_executed" in event_types
    assert "action_center_action_rolled_back" in event_types


def test_reject_blocks_pending_action() -> None:
    center = ActionCenter()
    action = center.create_action(
        agent_name="InventoryAgent",
        action_type="ad_boost",
        title="Boost ads despite low stock",
        description="Should be rejected by owner",
        risk_level=RiskLevel.HIGH,
        approval_mode=ApprovalMode.HARD_APPROVAL,
    )

    rejected = center.reject_action(action.action_id)
    assert rejected.status == ActionStatus.REJECTED

    executed = center.execute_action(action.action_id)
    assert executed.status == ActionStatus.REJECTED


def test_lists_pending_and_recent_actions() -> None:
    center = ActionCenter()
    first = center.create_action(
        agent_name="ContentAgent",
        action_type="content_update",
        title="Update title",
        description="Improve search terms",
    )
    second = center.create_action(
        agent_name="AdsAgent",
        action_type="bid_change",
        title="Change bid",
        description="Optimize ACOS",
        approval_mode=ApprovalMode.SOFT_APPROVAL,
    )
    center.reject_action(first.action_id)

    pending = center.list_pending_actions()
    recent = center.list_recent_actions()

    assert [action.action_id for action in pending] == [second.action_id]
    assert recent[0].action_id == second.action_id
    assert {action.action_id for action in recent} == {first.action_id, second.action_id}


def test_execution_requires_approval_when_approval_mode_is_not_none() -> None:
    center = ActionCenter()
    action = center.create_action(
        agent_name="AdsAgent",
        action_type="bid_change",
        title="Increase bid 20%",
        description="Risky bid increase",
        approval_mode=ApprovalMode.SOFT_APPROVAL,
    )

    executed = center.execute_action(action.action_id)

    assert executed.status == ActionStatus.PROPOSED
    assert executed.payload.get("mock_execution") is None

from zentory.actions.registry import ActionRegistry
from zentory.actions.schemas import Action
from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel
from zentory.decision.engine import DecisionEngine


def make_action() -> Action:
    return Action(action_type="mock", title="t", description="d")


def test_decision_engine_sets_approval_by_risk_level() -> None:
    engine = DecisionEngine()

    low = engine.decide({"risk_level": "LOW"}, [make_action()])
    medium = engine.decide({"risk_level": "MEDIUM"}, [make_action()])
    high = engine.decide({"risk_level": "HIGH"}, [make_action()])
    critical = engine.decide({"risk_level": "CRITICAL"}, [make_action()])

    assert low.approval_mode == ApprovalMode.NONE
    assert medium.approval_mode == ApprovalMode.SOFT_APPROVAL
    assert high.approval_mode == ApprovalMode.HARD_APPROVAL
    assert critical.approval_mode == ApprovalMode.HARD_APPROVAL
    assert critical.risk_level == RiskLevel.CRITICAL


def test_action_registry_can_approve_action() -> None:
    registry = ActionRegistry()
    action = registry.register(Action(action_type="mock", title="Mock", description="Mock"))

    approved = registry.approve(action.action_id)

    assert approved.status == ActionStatus.APPROVED

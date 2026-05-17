from typing import Any

from pydantic import BaseModel

from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.decision.policies import ApprovalPolicy
from zentory.decision.scoring import score_event_risk


class DecisionResult(BaseModel):
    risk_level: RiskLevel
    approval_mode: ApprovalMode
    proposed_actions: list[Action]


class DecisionEngine:
    def __init__(self, approval_policy: ApprovalPolicy | None = None) -> None:
        self.approval_policy = approval_policy or ApprovalPolicy()

    def decide(self, event: dict[str, Any], proposed_actions: list[Action]) -> DecisionResult:
        event_risk = score_event_risk(event)
        for action in proposed_actions:
            action.risk_level = self._max_risk(action.risk_level, event_risk)
            action.approval_mode = self.approval_policy.mode_for(action.risk_level)
        approval_mode = self.approval_policy.mode_for(event_risk)
        return DecisionResult(
            risk_level=event_risk,
            approval_mode=approval_mode,
            proposed_actions=proposed_actions,
        )

    @staticmethod
    def _max_risk(left: RiskLevel, right: RiskLevel) -> RiskLevel:
        order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        return max(left, right, key=order.index)

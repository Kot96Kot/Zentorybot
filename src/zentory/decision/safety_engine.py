from typing import Any

from pydantic import BaseModel, Field

from zentory.actions.action_limits import ActionLimits
from zentory.actions.schemas import Action
from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.risk_levels import max_risk
from zentory.decision.safety_rules import SafetyRules
from zentory.services.audit_service import AuditService


class SafetyDecision(BaseModel):
    action_id: str
    action_type: str
    automation_mode: AutomationMode
    risk_level: RiskLevel
    approval_mode: ApprovalMode
    requires_approval: bool
    requires_hard_approval: bool
    allowed_to_execute: bool
    blocked: bool = False
    status: ActionStatus
    reasons: list[str] = Field(default_factory=list)
    audit_id: str | None = None


class SafetyEngine:
    def __init__(
        self,
        mode: AutomationMode = AutomationMode.SHADOW,
        limits: ActionLimits | None = None,
        audit_service: AuditService | None = None,
        rules: SafetyRules | None = None,
    ) -> None:
        self.mode = mode
        self.limits = limits or ActionLimits()
        self.audit_service = audit_service or AuditService()
        self.rules = rules or SafetyRules(self.limits)

    def evaluate(self, action: Action, context: dict[str, Any] | None = None) -> SafetyDecision:
        rule_result = self.rules.evaluate(action)
        risk_level = max_risk(action.risk_level, rule_result.risk_level)
        approval_mode = self._approval_mode(risk_level, rule_result.approval_mode)
        requires_approval = approval_mode != ApprovalMode.NONE
        requires_hard_approval = approval_mode == ApprovalMode.HARD_APPROVAL
        blocked = rule_result.blocked
        allowed_to_execute = self._allowed_to_execute(
            risk_level=risk_level,
            requires_approval=requires_approval,
            blocked=blocked,
        )
        action.risk_level = risk_level
        action.approval_mode = approval_mode
        if not allowed_to_execute:
            action.status = ActionStatus.PROPOSED
        decision = SafetyDecision(
            action_id=action.action_id,
            action_type=action.action_type,
            automation_mode=self.mode,
            risk_level=risk_level,
            approval_mode=approval_mode,
            requires_approval=requires_approval,
            requires_hard_approval=requires_hard_approval,
            allowed_to_execute=allowed_to_execute,
            blocked=blocked,
            status=action.status,
            reasons=list(rule_result.reasons) + self._mode_reasons(allowed_to_execute, blocked),
        )
        audit_record = self.audit_service.record_action_decision(
            action_id=action.action_id,
            action_type=action.action_type,
            decision={
                "automation_mode": self.mode,
                "risk_level": risk_level,
                "approval_mode": approval_mode,
                "requires_approval": requires_approval,
                "requires_hard_approval": requires_hard_approval,
                "allowed_to_execute": allowed_to_execute,
                "blocked": blocked,
                "status": action.status,
                "reasons": decision.reasons,
                "context": context or {},
            },
        )
        decision.audit_id = str(audit_record["audit_id"])
        return decision

    def _allowed_to_execute(
        self, *, risk_level: RiskLevel, requires_approval: bool, blocked: bool
    ) -> bool:
        if blocked or self.mode in {AutomationMode.SHADOW, AutomationMode.ASSISTANT}:
            return False
        if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return False
        if self.mode == AutomationMode.SEMI_AUTO:
            return risk_level == RiskLevel.LOW and not requires_approval
        if self.mode == AutomationMode.AUTO:
            return not requires_approval
        return False

    @staticmethod
    def _approval_mode(risk_level: RiskLevel, rule_approval: ApprovalMode) -> ApprovalMode:
        if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return ApprovalMode.HARD_APPROVAL
        if rule_approval != ApprovalMode.NONE:
            return rule_approval
        if risk_level == RiskLevel.MEDIUM:
            return ApprovalMode.SOFT_APPROVAL
        return ApprovalMode.NONE

    def _mode_reasons(self, allowed_to_execute: bool, blocked: bool) -> list[str]:
        if blocked:
            return ["action is blocked by safety rules"]
        if self.mode == AutomationMode.SHADOW:
            return ["shadow mode records what would happen without execution"]
        if self.mode == AutomationMode.ASSISTANT:
            return ["assistant mode proposes actions without execution"]
        if not allowed_to_execute:
            return ["action requires approval before execution"]
        return ["action is allowed for mock execution"]

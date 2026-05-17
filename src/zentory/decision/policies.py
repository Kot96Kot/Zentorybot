from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.decision.approvals import approval_mode_for_risk


class ApprovalPolicy:
    def mode_for(self, risk_level: RiskLevel) -> ApprovalMode:
        return approval_mode_for_risk(risk_level)

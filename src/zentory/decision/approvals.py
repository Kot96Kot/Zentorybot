from zentory.core.enums import ApprovalMode, RiskLevel


def approval_mode_for_risk(risk_level: RiskLevel) -> ApprovalMode:
    if risk_level == RiskLevel.LOW:
        return ApprovalMode.NONE
    if risk_level == RiskLevel.MEDIUM:
        return ApprovalMode.SOFT_APPROVAL
    return ApprovalMode.HARD_APPROVAL

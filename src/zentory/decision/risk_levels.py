from zentory.core.enums import RiskLevel

RISK_ORDER: tuple[RiskLevel, ...] = (
    RiskLevel.LOW,
    RiskLevel.MEDIUM,
    RiskLevel.HIGH,
    RiskLevel.CRITICAL,
)


def max_risk(*levels: RiskLevel) -> RiskLevel:
    if not levels:
        return RiskLevel.LOW
    return max(levels, key=RISK_ORDER.index)

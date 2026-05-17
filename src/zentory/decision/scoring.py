from typing import Any

from zentory.core.enums import RiskLevel


def score_event_risk(event: dict[str, Any]) -> RiskLevel:
    explicit = event.get("risk_level") or event.get("payload", {}).get("risk_level")
    if explicit:
        return RiskLevel(str(explicit).upper())
    event_type = str(event.get("event_type", "")).lower()
    if "price" in event_type or "negative_review" in event_type:
        return RiskLevel.HIGH
    if "ads" in event_type or "promo" in event_type:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW

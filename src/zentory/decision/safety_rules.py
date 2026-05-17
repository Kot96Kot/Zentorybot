from dataclasses import dataclass
from typing import Any

from zentory.actions.action_limits import ActionLimits
from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode, RiskLevel


@dataclass(frozen=True, slots=True)
class SafetyRuleResult:
    risk_level: RiskLevel
    approval_mode: ApprovalMode
    reasons: tuple[str, ...] = ()
    blocked: bool = False


class SafetyRules:
    def __init__(self, limits: ActionLimits | None = None) -> None:
        self.limits = limits or ActionLimits()

    def evaluate(self, action: Action) -> SafetyRuleResult:
        payload = action.payload
        action_type = action.action_type
        if action_type == "price_change":
            return self._price_change(payload)
        if action_type == "ad_bid_increase":
            return self._ad_bid_increase(payload)
        if action_type == "promo_participation":
            return self._promo_participation(payload)
        if action_type in {"content_publish", "content_card_publish"}:
            return self._content_publish()
        if action_type == "content_bulk_update":
            return self._content_bulk_update(payload)
        if action_type in {"ad_budget_increase", "ad_campaign_boost", "ad_boost"}:
            return self._ad_boost(payload)
        return self._approval_for_risk(action.risk_level, reasons=("default action risk policy",))

    def _price_change(self, payload: dict[str, Any]) -> SafetyRuleResult:
        change = self.limits.price_change_percent(payload)
        new_price = float(payload.get("new_price", payload.get("price", 0)) or 0)
        minimum_margin = payload.get("minimum_margin_percent")
        new_margin = payload.get("new_margin_percent")
        if minimum_margin is not None and new_margin is not None:
            if float(new_margin) < float(minimum_margin):
                return SafetyRuleResult(
                    risk_level=RiskLevel.CRITICAL,
                    approval_mode=ApprovalMode.HARD_APPROVAL,
                    reasons=("new margin is below configured minimum margin",),
                    blocked=True,
                )
        cost_price = float(payload.get("cost_price", 0) or 0)
        mandatory_expenses = float(payload.get("mandatory_expenses", 0) or 0)
        if new_price and new_price < cost_price + mandatory_expenses:
            return SafetyRuleResult(
                risk_level=RiskLevel.CRITICAL,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                reasons=("new price is below cost plus mandatory expenses",),
                blocked=True,
            )
        if change > 15:
            return SafetyRuleResult(
                risk_level=RiskLevel.HIGH,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                reasons=(f"price change {change:.2f}% exceeds 15.00% hard approval limit",),
            )
        if change > self.limits.max_price_change_percent_without_approval:
            return SafetyRuleResult(
                risk_level=RiskLevel.MEDIUM,
                approval_mode=ApprovalMode.SOFT_APPROVAL,
                reasons=(f"price change {change:.2f}% exceeds 5.00% approval limit",),
            )
        return SafetyRuleResult(
            risk_level=RiskLevel.LOW,
            approval_mode=ApprovalMode.NONE,
            reasons=(f"price change {change:.2f}% is within 5.00% limit",),
        )

    def _ad_bid_increase(self, payload: dict[str, Any]) -> SafetyRuleResult:
        increase = self.limits.bid_increase_percent(payload)
        reasons = [f"bid increase {increase:.2f}% evaluated against 10.00% limit"]
        stock_days = float(payload.get("stock_days", self.limits.minimum_stock_days_for_ad_boost))
        if increase > 0 and stock_days < self.limits.minimum_stock_days_for_ad_boost:
            return SafetyRuleResult(
                risk_level=RiskLevel.CRITICAL,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                reasons=tuple(reasons + ["stock is below 7 days, ad strengthening is forbidden"]),
                blocked=True,
            )
        if increase > self.limits.max_bid_increase_percent_without_approval:
            return SafetyRuleResult(
                risk_level=RiskLevel.MEDIUM,
                approval_mode=ApprovalMode.SOFT_APPROVAL,
                reasons=tuple(reasons + ["bid increase exceeds approval limit"]),
            )
        return SafetyRuleResult(
            risk_level=RiskLevel.LOW,
            approval_mode=ApprovalMode.NONE,
            reasons=tuple(reasons + ["bid increase is within limit"]),
        )

    def _promo_participation(self, payload: dict[str, Any]) -> SafetyRuleResult:
        if int(payload.get("sku_count", 1) or 1) > 100:
            return SafetyRuleResult(
                risk_level=RiskLevel.HIGH,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                reasons=("bulk promo participation requires hard approval",),
            )
        if not self.limits.is_promo_margin_allowed(payload):
            margin = float(payload.get("margin_percent", payload.get("expected_margin_percent", 0)))
            return SafetyRuleResult(
                risk_level=RiskLevel.CRITICAL,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                reasons=(
                    f"promo margin {margin:.2f}% is below minimum "
                    f"{self.limits.minimum_promo_margin_percent:.2f}%",
                ),
                blocked=True,
            )
        return SafetyRuleResult(
            risk_level=RiskLevel.LOW,
            approval_mode=ApprovalMode.NONE,
            reasons=("promo margin is above minimum",),
        )

    @staticmethod
    def _content_publish() -> SafetyRuleResult:
        return SafetyRuleResult(
            risk_level=RiskLevel.HIGH,
            approval_mode=ApprovalMode.HARD_APPROVAL,
            reasons=("marketplace content publication is never automatic",),
            blocked=True,
        )

    @staticmethod
    def _content_bulk_update(payload: dict[str, Any]) -> SafetyRuleResult:
        sku_count = int(payload.get("sku_count", 1) or 1)
        if sku_count > 10:
            return SafetyRuleResult(
                risk_level=RiskLevel.HIGH,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                reasons=("bulk content update requires hard approval",),
            )
        return SafetyRuleResult(
            risk_level=RiskLevel.MEDIUM,
            approval_mode=ApprovalMode.SOFT_APPROVAL,
            reasons=("content update requires approval",),
        )

    def _ad_boost(self, payload: dict[str, Any]) -> SafetyRuleResult:
        if not self.limits.can_boost_ads_with_stock(payload):
            return SafetyRuleResult(
                risk_level=RiskLevel.CRITICAL,
                approval_mode=ApprovalMode.HARD_APPROVAL,
                reasons=("stock is below 7 days, ad strengthening is forbidden",),
                blocked=True,
            )
        return self._approval_for_risk(RiskLevel.LOW, reasons=("ad boost stock guard passed",))

    @staticmethod
    def _approval_for_risk(
        risk_level: RiskLevel, *, reasons: tuple[str, ...] = ()
    ) -> SafetyRuleResult:
        if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return SafetyRuleResult(risk_level, ApprovalMode.HARD_APPROVAL, reasons)
        if risk_level == RiskLevel.MEDIUM:
            return SafetyRuleResult(risk_level, ApprovalMode.SOFT_APPROVAL, reasons)
        return SafetyRuleResult(risk_level, ApprovalMode.NONE, reasons)

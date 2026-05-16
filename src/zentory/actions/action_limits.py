from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ActionLimits:
    max_price_change_percent_without_approval: float = 5.0
    max_bid_increase_percent_without_approval: float = 10.0
    minimum_promo_margin_percent: float = 20.0
    minimum_stock_days_for_ad_boost: int = 7

    def price_change_percent(self, payload: dict[str, Any]) -> float:
        if "change_percent" in payload:
            return abs(float(payload["change_percent"]))
        current_price = float(payload.get("current_price", 0) or 0)
        new_price = float(payload.get("new_price", current_price) or 0)
        if current_price <= 0:
            return 0.0
        return abs((new_price - current_price) / current_price * 100)

    def bid_increase_percent(self, payload: dict[str, Any]) -> float:
        if "increase_percent" in payload:
            return float(payload["increase_percent"])
        current_bid = float(payload.get("current_bid", 0) or 0)
        new_bid = float(payload.get("new_bid", current_bid) or 0)
        if current_bid <= 0:
            return 0.0
        return (new_bid - current_bid) / current_bid * 100

    def is_price_change_within_limit(self, payload: dict[str, Any]) -> bool:
        return self.price_change_percent(payload) <= self.max_price_change_percent_without_approval

    def is_bid_increase_within_limit(self, payload: dict[str, Any]) -> bool:
        return self.bid_increase_percent(payload) <= self.max_bid_increase_percent_without_approval

    def is_promo_margin_allowed(self, payload: dict[str, Any]) -> bool:
        margin = float(payload.get("margin_percent", payload.get("expected_margin_percent", 100)))
        return margin >= self.minimum_promo_margin_percent

    def can_boost_ads_with_stock(self, payload: dict[str, Any]) -> bool:
        stock_days = float(payload.get("stock_days", self.minimum_stock_days_for_ad_boost))
        return stock_days >= self.minimum_stock_days_for_ad_boost

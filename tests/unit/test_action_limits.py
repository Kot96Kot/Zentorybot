from zentory.actions.action_limits import ActionLimits


def test_price_change_limit_uses_percent_payload() -> None:
    limits = ActionLimits()

    assert limits.price_change_percent({"change_percent": 3}) == 3
    assert limits.is_price_change_within_limit({"change_percent": 3}) is True
    assert limits.is_price_change_within_limit({"change_percent": 12}) is False


def test_bid_increase_limit_can_be_calculated_from_bids() -> None:
    limits = ActionLimits()

    payload = {"current_bid": 100, "new_bid": 120}

    assert limits.bid_increase_percent(payload) == 20
    assert limits.is_bid_increase_within_limit(payload) is False


def test_promo_margin_and_stock_guards() -> None:
    limits = ActionLimits(minimum_promo_margin_percent=20, minimum_stock_days_for_ad_boost=7)

    assert limits.is_promo_margin_allowed({"margin_percent": 19}) is False
    assert limits.is_promo_margin_allowed({"margin_percent": 20}) is True
    assert limits.can_boost_ads_with_stock({"stock_days": 6}) is False
    assert limits.can_boost_ads_with_stock({"stock_days": 7}) is True

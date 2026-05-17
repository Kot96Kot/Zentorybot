from zentory.services.seasonality_service import SeasonalityService


def test_category_month_coefficient_is_applied() -> None:
    assert SeasonalityService().coefficient_for(category="cosmetics", month="12") == 1.35


def test_unknown_category_uses_default() -> None:
    assert SeasonalityService().coefficient_for(category="unknown", month="12") == 1.0


def test_sku_coefficient_overrides_category() -> None:
    assert (
        SeasonalityService().coefficient_for(category="cosmetics", month="12", sku="ZNT-COS-001")
        == 1.45
    )


def test_trend_coefficient_is_limited() -> None:
    service = SeasonalityService()

    assert service.trend_coefficient(recent_avg_daily_sales=10, previous_avg_daily_sales=1) == 1.5
    assert service.trend_coefficient(recent_avg_daily_sales=1, previous_avg_daily_sales=10) == 0.7
    assert service.trend_coefficient(recent_avg_daily_sales=5, previous_avg_daily_sales=5) == 1.0


def test_seasonality_result_exposes_category_month_and_sku_coefficients() -> None:
    result = SeasonalityService().build_result(
        category="cosmetics",
        month=11,
        sku="ZNT-COS-001",
        recent_avg_daily_sales=4,
        previous_avg_daily_sales=3.2,
    )

    assert result.category_coefficient == 1.0
    assert result.month_coefficient == 1.25
    assert result.sku_coefficient == 1.08
    assert result.seasonality_coefficient == 1.35
    assert 0.7 <= result.trend_coefficient <= 1.5

from zentory.schemas.sales_plan import MarketplaceArticle, SalesPlanInput, SalesPlanStatus
from zentory.services.sales_plan_service import SalesPlanService


def _sales_plan(**overrides: object) -> SalesPlanInput:
    data = {
        "sku": "SKU-PLAN-1",
        "marketplace_articles": [MarketplaceArticle(marketplace="wildberries", article="WB-1")],
        "current_sales": 10,
        "sales_7d": 70,
        "sales_14d": 140,
        "sales_30d": 300,
        "stock": 120,
        "average_price": 1_000.0,
        "target_revenue": 300_000.0,
        "target_margin": 0.25,
        "ad_spend": 20_000.0,
        "impressions": 10_000,
        "seasonal_coefficient": 1.0,
        "drr_limit": 0.18,
    }
    data.update(overrides)
    return SalesPlanInput(**data)


def test_sales_plan_uses_inventory_for_stock_days() -> None:
    report = SalesPlanService().calculate_report(_sales_plan(stock=20))

    assert report.stock_days_left is not None
    assert report.stock_days_left < 14
    assert report.alerts


def test_sales_plan_uses_average_sales_speed_for_day_plan() -> None:
    report = SalesPlanService().calculate_report(
        _sales_plan(sales_7d=140, sales_14d=210, sales_30d=300)
    )

    assert report.day_plan >= 20


def test_unreachable_plan_due_to_stock_creates_warning() -> None:
    report = SalesPlanService().calculate_report(_sales_plan(stock=5, current_sales=1))

    assert report.status in {SalesPlanStatus.WARNING, SalesPlanStatus.CRITICAL}
    assert any("Остатка" in alert for alert in report.alerts)


def test_unreachable_plan_due_to_ads_or_conversion_creates_action_recommendation() -> None:
    report = SalesPlanService().calculate_report(
        _sales_plan(current_sales=0, impressions=20_000, ad_spend=100_000, target_revenue=300_000)
    )

    assert report.tasks or report.recommendations
    assert any("карточки" in task or "реклам" in item for task in report.tasks for item in [task])

from zentory.schemas.forecast import AggregatedSkuSnapshot, StockStatus
from zentory.services.stock_forecast_service import StockForecastService


def _item(**overrides: object) -> AggregatedSkuSnapshot:
    data = {
        "sku": "SKU-1",
        "nm_id": 1,
        "vendor_code": "V-1",
        "product_name": "Product",
        "category": "cosmetics",
        "stock_by_warehouse": {"W1": 100},
        "stock_by_region": {"Центр": 100},
        "total_stock": 100,
        "sales_qty_7d": 14,
        "sales_qty_14d": 28,
        "sales_qty_30d": 60,
        "revenue_30d": 6000,
        "buyout_percent": 0.9,
        "price": 100,
        "cost": 50,
        "advertising_spend": 100,
        "returns_qty": 0,
        "active_sales_days_7d": 7,
        "active_sales_days_14d": 14,
        "active_sales_days_30d": 15,
        "recent_avg_daily_sales": 4,
        "previous_avg_daily_sales": 2,
    }
    data.update(overrides)
    return AggregatedSkuSnapshot(**data)


def test_average_daily_sales_uses_active_days_instead_of_calendar_days() -> None:
    avg = StockForecastService().calculate_avg_daily_sales(_item())

    assert avg.avg_daily_sales_30d == 4
    assert avg.selected_avg_daily_sales == 4


def test_average_daily_sales_fallback_warns_when_active_days_missing() -> None:
    avg = StockForecastService().calculate_avg_daily_sales(_item(active_sales_days_30d=None))

    assert avg.avg_daily_sales_30d == 2
    assert "Расчет сделан без учета out-of-stock дней" in avg.warnings


def test_zero_sales_has_no_division_by_zero() -> None:
    forecast = StockForecastService().forecast_item(
        _item(sales_qty_7d=0, sales_qty_14d=0, sales_qty_30d=0, active_sales_days_30d=30)
    )

    assert forecast.avg_daily_sales == 0
    assert forecast.stock_coverage_days is None
    assert forecast.stock_status == StockStatus.NO_SALES


def test_stock_status_critical_and_out_of_stock() -> None:
    service = StockForecastService()

    critical = service.forecast_item(_item(total_stock=20))
    out_of_stock = service.forecast_item(_item(total_stock=0))

    assert critical.stock_status == StockStatus.CRITICAL
    assert out_of_stock.stock_status == StockStatus.OUT_OF_STOCK


def test_forecast_uses_seasonality_and_trend_coefficients() -> None:
    forecast = StockForecastService().forecast_item(_item(), month=11)

    assert forecast.avg_daily_sales_7d == 2
    assert forecast.avg_daily_sales_14d == 2
    assert forecast.avg_daily_sales_30d == 4
    assert forecast.avg_daily_sales == 4
    assert forecast.seasonality_coefficient == 1.25
    assert forecast.trend_coefficient == 1.5
    assert forecast.forecast_sales_30 == 225
    assert forecast.forecast_sales_60 == 450
    assert forecast.forecast_sales_90 == 675


def test_negative_sales_input_does_not_produce_negative_forecast() -> None:
    forecast = StockForecastService().forecast_item(
        _item(sales_qty_7d=-7, sales_qty_14d=-14, sales_qty_30d=-30)
    )

    assert forecast.avg_daily_sales == 0
    assert forecast.forecast_sales_30 == 0
    assert forecast.forecast_sales_60 == 0
    assert forecast.forecast_sales_90 == 0

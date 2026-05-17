import asyncio

from zentory.api.routers.analytics import (
    abc_by_metric,
    abc_default,
    forecast,
    forecast_sku,
    stock_forecast,
)
from zentory.schemas.abc import ABCMetric
from zentory.services.forecast_service import ForecastService


def test_analytics_routes_return_mock_forecast_abc_contracts() -> None:
    service = ForecastService()

    abc = asyncio.run(abc_default(service))
    abc_profit = asyncio.run(abc_by_metric(ABCMetric.PROFIT, service))
    full = asyncio.run(forecast(service))
    sku = asyncio.run(forecast_sku("ZNT-COS-001", service))
    stock = asyncio.run(stock_forecast(service))

    assert abc["mock_mode"] is True
    assert abc["metric"] == "revenue"
    assert abc["rows"][0]["share"] > 0
    assert abc_profit["metric"] == "profit"
    assert full["abc"]["rows"]
    assert full["seasonality"][0]["category_coefficient"] > 0
    assert sku["forecast"]["sku"] == "ZNT-COS-001"
    assert sku["forecast"]["avg_daily_sales_30d"] > 0
    assert stock["items"][0]["forecast_sales_90"] > 0

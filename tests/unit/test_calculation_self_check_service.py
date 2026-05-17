from zentory.schemas.abc import (
    ABCAnalysisInput,
    ABCAnalysisReport,
    ABCAnalysisRow,
    ABCClass,
    ABCMetric,
)
from zentory.schemas.forecast import (
    SelfCheckResult,
    StockForecastItem,
    StockForecastReport,
    StockStatus,
)
from zentory.services.calculation_self_check_service import CalculationSelfCheckService


def test_self_check_catches_negative_sales_and_revenue() -> None:
    report = ABCAnalysisReport(
        metric=ABCMetric.REVENUE,
        total_metric=0,
        rows=[],
        warnings=[],
        mock_mode=True,
    )

    result = CalculationSelfCheckService().check_abc(
        input_items=[ABCAnalysisInput(sku="BAD", product_name="Bad", sales_qty=-1, revenue=-1)],
        report=report,
    )

    assert result.passed is False
    assert any("sales_qty" in error for error in result.errors)
    assert any("revenue" in error for error in result.errors)
    assert result.warnings


def test_self_check_catches_wrong_abc_share_sum_and_lost_mapping() -> None:
    report = ABCAnalysisReport(
        metric=ABCMetric.REVENUE,
        total_metric=100,
        rows=[
            ABCAnalysisRow(
                sku="A",
                product_name="A",
                metric_value=50,
                share_percent=40,
                cumulative_share_percent=40,
                abc_class=ABCClass.A,
                rank=1,
            )
        ],
        mock_mode=True,
    )

    result = CalculationSelfCheckService().check_abc(
        input_items=[ABCAnalysisInput(sku="A", product_name="A", revenue=100)],
        report=report,
        mapping_skus=set(),
    )

    assert result.passed is False
    assert any("Сумма долей ABC" in error for error in result.errors)
    assert any("mapping" in warning for warning in result.warnings)


def test_self_check_catches_negative_stock() -> None:
    item = StockForecastItem(
        sku="BAD",
        product_name="Bad",
        total_stock=-1,
        avg_daily_sales=1,
        forecast_sales_30=30,
        forecast_sales_60=60,
        forecast_sales_90=90,
        stock_status=StockStatus.OK,
        recommended_replenishment_qty_30=0,
        recommended_replenishment_qty_60=0,
        recommended_replenishment_qty_90=0,
        seasonality_coefficient=1,
        trend_coefficient=1,
    )

    result = CalculationSelfCheckService().check_items([item])

    assert result.passed is False
    assert any("total_stock" in error for error in result.errors)


def test_forecast_self_check_returns_false_on_critical_errors() -> None:
    report = StockForecastReport(
        items=[
            StockForecastItem(
                sku="BAD",
                product_name="Bad",
                total_stock=1,
                avg_daily_sales=-1,
                forecast_sales_30=30,
                forecast_sales_60=60,
                forecast_sales_90=90,
                stock_status=StockStatus.OK,
                recommended_replenishment_qty_30=0,
                recommended_replenishment_qty_60=0,
                recommended_replenishment_qty_90=0,
                seasonality_coefficient=1,
                trend_coefficient=1,
            )
        ],
        self_check=SelfCheckResult(passed=True),
    )

    result = CalculationSelfCheckService().check_forecast(input_items=[], report=report)

    assert result.passed is False
    assert result.errors

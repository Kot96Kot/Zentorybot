from math import ceil

from zentory.schemas.forecast import (
    AggregatedSkuSnapshot,
    AvgDailySales,
    SelfCheckResult,
    StockForecastItem,
    StockForecastReport,
    StockStatus,
)
from zentory.schemas.seasonality import SeasonalityResult
from zentory.services.seasonality_service import SeasonalityService


class StockForecastService:
    def __init__(self, seasonality_service: SeasonalityService | None = None) -> None:
        self.seasonality_service = seasonality_service or SeasonalityService()

    def calculate_avg_daily_sales(self, item: AggregatedSkuSnapshot) -> AvgDailySales:
        warnings: list[str] = []
        avg_7 = self._safe_average(item.sales_qty_7d, item.active_sales_days_7d, 7, warnings)
        avg_14 = self._safe_average(item.sales_qty_14d, item.active_sales_days_14d, 14, warnings)
        avg_30 = self._safe_average(item.sales_qty_30d, item.active_sales_days_30d, 30, warnings)
        return AvgDailySales(
            sku=item.sku,
            avg_daily_sales_7d=round(avg_7, 4),
            avg_daily_sales_14d=round(avg_14, 4),
            avg_daily_sales_30d=round(avg_30, 4),
            selected_avg_daily_sales=round(avg_30, 4),
            warnings=warnings,
            mock_mode=True,
        )

    def forecast_item(self, item: AggregatedSkuSnapshot, *, month: int = 11) -> StockForecastItem:
        avg = self.calculate_avg_daily_sales(item)
        seasonality = self.seasonality_service.build_result(
            category=item.category,
            month=month,
            sku=item.sku,
            recent_avg_daily_sales=item.recent_avg_daily_sales or avg.avg_daily_sales_7d,
            previous_avg_daily_sales=item.previous_avg_daily_sales or avg.avg_daily_sales_30d,
        )
        avg_daily_sales = avg.selected_avg_daily_sales
        if item.total_stock == 0:
            status = StockStatus.OUT_OF_STOCK
        elif avg_daily_sales == 0:
            status = StockStatus.NO_SALES
        else:
            coverage = item.total_stock / avg_daily_sales
            if coverage < 14:
                status = StockStatus.CRITICAL
            elif coverage <= 30:
                status = StockStatus.WARNING
            else:
                status = StockStatus.OK
        coverage_days = (
            None if avg_daily_sales == 0 else round(item.total_stock / avg_daily_sales, 2)
        )
        forecast_30 = self._forecast(avg_daily_sales, 30, seasonality)
        forecast_60 = self._forecast(avg_daily_sales, 60, seasonality)
        forecast_90 = self._forecast(avg_daily_sales, 90, seasonality)
        return StockForecastItem(
            sku=item.sku,
            product_name=item.product_name,
            total_stock=item.total_stock,
            avg_daily_sales=avg_daily_sales,
            forecast_sales_30=forecast_30,
            forecast_sales_60=forecast_60,
            forecast_sales_90=forecast_90,
            stock_coverage_days=coverage_days,
            stock_status=status,
            recommended_replenishment_qty_30=max(0, ceil(forecast_30 - item.total_stock)),
            recommended_replenishment_qty_60=max(0, ceil(forecast_60 - item.total_stock)),
            recommended_replenishment_qty_90=max(0, ceil(forecast_90 - item.total_stock)),
            seasonality_coefficient=seasonality.seasonality_coefficient,
            trend_coefficient=seasonality.trend_coefficient,
            warnings=avg.warnings,
            mock_mode=True,
        )

    def forecast(
        self, items: list[AggregatedSkuSnapshot], *, month: int = 11
    ) -> StockForecastReport:
        forecast_items = [self.forecast_item(item, month=month) for item in items]
        return StockForecastReport(
            items=forecast_items,
            self_check=SelfCheckResult(
                passed=True,
                errors=[],
                warnings=[warning for item in forecast_items for warning in item.warnings],
                checked_rules_count=0,
                mock_mode=True,
            ),
            mock_mode=True,
        )

    @staticmethod
    def _safe_average(
        sales_qty: int, active_days: int | None, fallback_days: int, warnings: list[str]
    ) -> float:
        safe_sales_qty = max(sales_qty, 0)
        if active_days is None:
            warnings.append("Расчет сделан без учета out-of-stock дней")
            return safe_sales_qty / fallback_days if fallback_days > 0 else 0
        if active_days <= 0:
            return 0
        return safe_sales_qty / active_days

    @staticmethod
    def _forecast(avg_daily_sales: float, days: int, seasonality: SeasonalityResult) -> float:
        forecast = (
            avg_daily_sales
            * days
            * seasonality.seasonality_coefficient
            * seasonality.trend_coefficient
        )
        return round(max(forecast, 0), 2)

from math import isclose

from zentory.schemas.abc import ABCAnalysisInput, ABCAnalysisReport
from zentory.schemas.forecast import (
    AggregatedSkuSnapshot,
    SelfCheckResult,
    StockForecastItem,
    StockForecastReport,
)


class CalculationSelfCheckService:
    def check_abc(
        self,
        *,
        input_items: list[ABCAnalysisInput],
        report: ABCAnalysisReport,
        mapping_skus: set[str] | None = None,
    ) -> SelfCheckResult:
        errors: list[str] = []
        warnings: list[str] = list(report.warnings)
        checked_rules_count = 0

        checked_rules_count += 1
        if len(input_items) != len(report.rows):
            errors.append("Количество SKU на входе не равно количеству строк ABC на выходе")

        checked_rules_count += 1
        if report.total_metric == 0:
            warnings.append("ABC total_metric=0: нужен ручной анализ нулевой метрики")
        elif not isclose(sum(row.share_percent for row in report.rows), 100.0, abs_tol=0.05):
            errors.append("Сумма долей ABC не равна примерно 100%")

        checked_rules_count += 1
        cumulative_values = [row.cumulative_share_percent for row in report.rows]
        pairs = zip(cumulative_values, cumulative_values[1:], strict=False)
        if any(current < previous for previous, current in pairs):
            errors.append("ABC cumulative_share уменьшается от строки к строке")

        checked_rules_count += 1
        for item in input_items:
            if item.sales_qty < 0:
                errors.append(f"SKU {item.sku}: sales_qty отрицательный")
            if item.revenue < 0:
                errors.append(f"SKU {item.sku}: revenue отрицательная")

        checked_rules_count += 1
        if mapping_skus is not None:
            input_skus = {item.sku for item in input_items}
            missing = sorted(input_skus - mapping_skus)
            if missing:
                warnings.append(f"SKU потерялись в mapping: {', '.join(missing)}")

        checked_rules_count += 1
        if not report.mock_mode:
            errors.append("Mock-отчет должен явно иметь mock_mode=true")

        return SelfCheckResult(
            passed=not errors,
            errors=errors,
            warnings=warnings,
            checked_rules_count=checked_rules_count,
            mock_mode=True,
        )

    def check_forecast(
        self,
        *,
        input_items: list[AggregatedSkuSnapshot],
        report: StockForecastReport,
    ) -> SelfCheckResult:
        errors: list[str] = []
        warnings: list[str] = list(report.self_check.warnings)
        checked_rules_count = 0

        checked_rules_count += 1
        if len(input_items) != len(report.items):
            errors.append("Количество SKU на входе не равно количеству прогнозов на выходе")

        checked_rules_count += 1
        by_sku = {item.sku: item for item in input_items}
        for forecast in report.items:
            source = by_sku.get(forecast.sku)
            if source is None:
                warnings.append(f"SKU {forecast.sku} потерялся в исходных данных")
                continue
            if source.total_stock < 0:
                errors.append(f"SKU {source.sku}: total_stock отрицательный")
            if source.sales_qty_30d < 0:
                errors.append(f"SKU {source.sku}: sales_qty отрицательный")
            if source.revenue_30d < 0:
                errors.append(f"SKU {source.sku}: revenue отрицательная")

        checked_rules_count += 1
        for forecast in report.items:
            if forecast.avg_daily_sales < 0:
                errors.append(f"SKU {forecast.sku}: avg_daily_sales отрицательный")
            if min(
                forecast.forecast_sales_30,
                forecast.forecast_sales_60,
                forecast.forecast_sales_90,
            ) < 0:
                errors.append(f"SKU {forecast.sku}: forecast_sales отрицательный")
            if forecast.avg_daily_sales == 0 and forecast.stock_coverage_days is not None:
                errors.append(f"SKU {forecast.sku}: avg_daily_sales=0, но coverage не null")

        checked_rules_count += 1
        if not report.mock_mode:
            errors.append("Forecast-отчет должен явно иметь mock_mode=true")

        return SelfCheckResult(
            passed=not errors,
            errors=errors,
            warnings=warnings,
            checked_rules_count=checked_rules_count,
            mock_mode=True,
        )

    def check_items(self, items: list[StockForecastItem]) -> SelfCheckResult:
        errors: list[str] = []
        checked_rules_count = 0
        for item in items:
            checked_rules_count += 1
            if item.total_stock < 0:
                errors.append(f"SKU {item.sku}: total_stock отрицательный")
            if item.avg_daily_sales < 0:
                errors.append(f"SKU {item.sku}: avg_daily_sales отрицательный")
        return SelfCheckResult(
            passed=not errors,
            errors=errors,
            warnings=[],
            checked_rules_count=checked_rules_count,
            mock_mode=True,
        )

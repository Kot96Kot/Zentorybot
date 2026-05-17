from collections import defaultdict

from zentory.schemas.abc import ABCAnalysisInput, ABCMetric
from zentory.schemas.forecast import (
    AggregatedSkuSnapshot,
    ForecastABCReport,
    MarketplaceSalesProvider,
    MarketplaceSkuSnapshot,
    SelfCheckResult,
)
from zentory.services.abc_analysis_service import ABCAnalysisService
from zentory.services.calculation_self_check_service import CalculationSelfCheckService
from zentory.services.seasonality_service import SeasonalityService
from zentory.services.stock_forecast_service import StockForecastService


class MockMarketplaceSalesProvider:
    def fetch_sales_by_sku(self, date_from: str, date_to: str) -> list[MarketplaceSkuSnapshot]:
        return self.fetch_stocks_by_warehouse()

    def fetch_orders_by_sku(self, date_from: str, date_to: str) -> list[dict]:
        return [
            {"sku": "ZNT-COS-001", "orders_30d": 96, "mock": True},
            {"sku": "ZNT-HOME-002", "orders_30d": 48, "mock": True},
            {"sku": "ZNT-ACC-003", "orders_30d": 9, "mock": True},
        ]

    def fetch_stocks_by_warehouse(self) -> list[MarketplaceSkuSnapshot]:
        return [
            MarketplaceSkuSnapshot(
                sku="ZNT-COS-001",
                nm_id=100001,
                vendor_code="COS-001",
                product_name="Крем для рук Zentory",
                category="cosmetics",
                warehouse_name="Коледино",
                region="Центр",
                stock_qty=80,
                sales_qty_7d=28,
                sales_qty_14d=52,
                sales_qty_30d=96,
                revenue_30d=144_000,
                buyout_percent=0.92,
                price=1500,
                cost=740,
                advertising_spend=12_000,
                returns_qty=4,
                active_sales_days_7d=7,
                active_sales_days_14d=14,
                active_sales_days_30d=24,
                recent_avg_daily_sales=4.0,
                previous_avg_daily_sales=3.2,
            ),
            MarketplaceSkuSnapshot(
                sku="ZNT-COS-001",
                nm_id=100001,
                vendor_code="COS-001",
                product_name="Крем для рук Zentory",
                category="cosmetics",
                warehouse_name="Казань",
                region="Поволжье",
                stock_qty=45,
                sales_qty_7d=28,
                sales_qty_14d=52,
                sales_qty_30d=96,
                revenue_30d=144_000,
                buyout_percent=0.92,
                price=1500,
                cost=740,
                advertising_spend=12_000,
                returns_qty=4,
                active_sales_days_7d=7,
                active_sales_days_14d=14,
                active_sales_days_30d=24,
                recent_avg_daily_sales=4.0,
                previous_avg_daily_sales=3.2,
            ),
            MarketplaceSkuSnapshot(
                sku="ZNT-HOME-002",
                nm_id=100002,
                vendor_code="HOME-002",
                product_name="Органайзер Zentory Home",
                category="home",
                warehouse_name="Хоругвино",
                region="Центр",
                stock_qty=420,
                sales_qty_7d=14,
                sales_qty_14d=25,
                sales_qty_30d=48,
                revenue_30d=95_520,
                buyout_percent=0.88,
                price=1990,
                cost=900,
                advertising_spend=8_500,
                returns_qty=3,
                active_sales_days_7d=7,
                active_sales_days_14d=14,
                active_sales_days_30d=30,
                recent_avg_daily_sales=2.0,
                previous_avg_daily_sales=1.6,
            ),
            MarketplaceSkuSnapshot(
                sku="ZNT-ACC-003",
                nm_id=100003,
                vendor_code="ACC-003",
                product_name="Аксессуар Zentory",
                category="accessories",
                warehouse_name="Софьино",
                region="Центр",
                stock_qty=0,
                sales_qty_7d=0,
                sales_qty_14d=3,
                sales_qty_30d=9,
                revenue_30d=17_910,
                buyout_percent=0.8,
                price=1990,
                cost=1200,
                advertising_spend=2_000,
                returns_qty=1,
                active_sales_days_7d=0,
                active_sales_days_14d=5,
                active_sales_days_30d=15,
                recent_avg_daily_sales=0.0,
                previous_avg_daily_sales=0.6,
            ),
        ]

    def fetch_stock_movements(self) -> list[dict]:
        return [{"sku": "ZNT-COS-001", "movement": "mock_supply", "qty": 50, "mock": True}]

    def fetch_product_mapping(self) -> dict[str, dict]:
        return {
            "ZNT-COS-001": {"nm_id": 100001, "vendor_code": "COS-001", "mock": True},
            "ZNT-HOME-002": {"nm_id": 100002, "vendor_code": "HOME-002", "mock": True},
            "ZNT-ACC-003": {"nm_id": 100003, "vendor_code": "ACC-003", "mock": True},
        }


class ForecastService:
    def __init__(
        self,
        provider: MarketplaceSalesProvider | None = None,
        abc_service: ABCAnalysisService | None = None,
        stock_forecast_service: StockForecastService | None = None,
        self_check_service: CalculationSelfCheckService | None = None,
        seasonality_service: SeasonalityService | None = None,
    ) -> None:
        self.provider = provider or MockMarketplaceSalesProvider()
        self.abc_service = abc_service or ABCAnalysisService()
        self.stock_forecast_service = stock_forecast_service or StockForecastService()
        self.self_check_service = self_check_service or CalculationSelfCheckService()
        self.seasonality_service = seasonality_service or SeasonalityService()

    def load_aggregated_skus(self) -> list[AggregatedSkuSnapshot]:
        rows = self.provider.fetch_stocks_by_warehouse()
        grouped: dict[str, list[MarketplaceSkuSnapshot]] = defaultdict(list)
        for row in rows:
            grouped[row.sku].append(row)

        aggregated: list[AggregatedSkuSnapshot] = []
        for sku, sku_rows in grouped.items():
            first = sku_rows[0]
            stock_by_warehouse: dict[str, int] = defaultdict(int)
            stock_by_region: dict[str, int] = defaultdict(int)
            for row in sku_rows:
                stock_by_warehouse[row.warehouse_name] += row.stock_qty
                stock_by_region[row.region] += row.stock_qty
            aggregated.append(
                AggregatedSkuSnapshot(
                    sku=sku,
                    nm_id=first.nm_id,
                    vendor_code=first.vendor_code,
                    product_name=first.product_name,
                    category=first.category,
                    stock_by_warehouse=dict(stock_by_warehouse),
                    stock_by_region=dict(stock_by_region),
                    total_stock=sum(stock_by_warehouse.values()),
                    sales_qty_7d=first.sales_qty_7d,
                    sales_qty_14d=first.sales_qty_14d,
                    sales_qty_30d=first.sales_qty_30d,
                    revenue_30d=first.revenue_30d,
                    buyout_percent=first.buyout_percent,
                    price=first.price,
                    cost=first.cost,
                    advertising_spend=first.advertising_spend,
                    returns_qty=first.returns_qty,
                    active_sales_days_7d=first.active_sales_days_7d,
                    active_sales_days_14d=first.active_sales_days_14d,
                    active_sales_days_30d=first.active_sales_days_30d,
                    recent_avg_daily_sales=first.recent_avg_daily_sales,
                    previous_avg_daily_sales=first.previous_avg_daily_sales,
                    mock=True,
                )
            )
        return aggregated

    def abc_report(self, metric: ABCMetric | str = ABCMetric.REVENUE):
        items = self.load_aggregated_skus()
        abc_inputs = [
            ABCAnalysisInput(
                sku=item.sku,
                product_name=item.product_name,
                revenue=item.revenue_30d,
                profit=item.profit_30d,
                sales_qty=item.sales_qty_30d,
            )
            for item in items
        ]
        report = self.abc_service.analyze(abc_inputs, metric=metric)
        self_check = self.self_check_service.check_abc(
            input_items=abc_inputs,
            report=report,
            mapping_skus=set(self.provider.fetch_product_mapping()),
        )
        report.warnings.extend(
            warning for warning in self_check.warnings if warning not in report.warnings
        )
        return report

    def stock_forecast_report(self, *, month: int = 11):
        items = self.load_aggregated_skus()
        report = self.stock_forecast_service.forecast(items, month=month)
        report.self_check = self.self_check_service.check_forecast(input_items=items, report=report)
        return report

    def full_report(
        self, metric: ABCMetric | str = ABCMetric.REVENUE, *, month: int = 11
    ) -> ForecastABCReport:
        items = self.load_aggregated_skus()
        abc_inputs = [
            ABCAnalysisInput(
                sku=item.sku,
                product_name=item.product_name,
                revenue=item.revenue_30d,
                profit=item.profit_30d,
                sales_qty=item.sales_qty_30d,
            )
            for item in items
        ]
        abc = self.abc_service.analyze(abc_inputs, metric=metric)
        stock = self.stock_forecast_service.forecast(items, month=month)
        abc_check = self.self_check_service.check_abc(
            input_items=abc_inputs,
            report=abc,
            mapping_skus=set(self.provider.fetch_product_mapping()),
        )
        stock.self_check = self.self_check_service.check_forecast(input_items=items, report=stock)
        errors = abc_check.errors + stock.self_check.errors
        warnings = abc_check.warnings + stock.self_check.warnings
        combined = SelfCheckResult(
            passed=not errors,
            errors=errors,
            warnings=warnings,
            checked_rules_count=(
                abc_check.checked_rules_count + stock.self_check.checked_rules_count
            ),
            mock_mode=True,
        )
        seasonality = [
            self.seasonality_service.build_result(
                category=item.category,
                month=month,
                sku=item.sku,
                recent_avg_daily_sales=item.recent_avg_daily_sales or 0,
                previous_avg_daily_sales=item.previous_avg_daily_sales or 0,
            )
            for item in items
        ]
        recommendation = (
            "Расчет требует проверки человеком"
            if not combined.passed
            else "Mock forecast готов: проверьте A-SKU и critical stock перед закупкой"
        )
        return ForecastABCReport(
            abc=abc,
            stock_forecast=stock,
            seasonality=seasonality,
            self_check=combined,
            recommendation=recommendation,
            mock_mode=True,
        )

    def sku_forecast(self, sku: str, *, month: int = 11):
        report = self.stock_forecast_report(month=month)
        return next((item for item in report.items if item.sku == sku), None)

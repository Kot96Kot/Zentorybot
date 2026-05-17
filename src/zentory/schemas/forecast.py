from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field

from zentory.schemas.abc import ABCAnalysisReport
from zentory.schemas.seasonality import SeasonalityResult


class StockStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    OUT_OF_STOCK = "out_of_stock"
    NO_SALES = "no_sales"


class SelfCheckResult(BaseModel):
    passed: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checked_rules_count: int = 0
    mock_mode: bool = True


class MarketplaceSkuSnapshot(BaseModel):
    sku: str
    nm_id: int
    vendor_code: str
    product_name: str
    category: str = "default"
    warehouse_name: str
    region: str = "unknown"
    stock_qty: int
    sales_qty_7d: int
    sales_qty_14d: int
    sales_qty_30d: int
    revenue_30d: float
    buyout_percent: float
    price: float
    cost: float
    advertising_spend: float
    returns_qty: int
    active_sales_days_7d: int | None = None
    active_sales_days_14d: int | None = None
    active_sales_days_30d: int | None = None
    recent_avg_daily_sales: float | None = None
    previous_avg_daily_sales: float | None = None
    mock: bool = True


class AggregatedSkuSnapshot(BaseModel):
    sku: str
    nm_id: int
    vendor_code: str
    product_name: str
    category: str = "default"
    stock_by_warehouse: dict[str, int] = Field(default_factory=dict)
    stock_by_region: dict[str, int] = Field(default_factory=dict)
    total_stock: int
    sales_qty_7d: int
    sales_qty_14d: int
    sales_qty_30d: int
    revenue_30d: float
    buyout_percent: float
    price: float
    cost: float
    advertising_spend: float
    returns_qty: int
    active_sales_days_7d: int | None = None
    active_sales_days_14d: int | None = None
    active_sales_days_30d: int | None = None
    recent_avg_daily_sales: float | None = None
    previous_avg_daily_sales: float | None = None
    mock: bool = True

    @property
    def profit_30d(self) -> float:
        gross_profit = (self.price - self.cost) * self.sales_qty_30d
        return gross_profit - self.advertising_spend


class AvgDailySales(BaseModel):
    sku: str
    avg_daily_sales_7d: float
    avg_daily_sales_14d: float
    avg_daily_sales_30d: float
    selected_avg_daily_sales: float
    warnings: list[str] = Field(default_factory=list)
    mock_mode: bool = True


class StockForecastItem(BaseModel):
    sku: str
    product_name: str
    total_stock: int
    avg_daily_sales: float
    forecast_sales_30: float
    forecast_sales_60: float
    forecast_sales_90: float
    stock_coverage_days: float | None = None
    stock_status: StockStatus
    recommended_replenishment_qty_30: int
    recommended_replenishment_qty_60: int
    recommended_replenishment_qty_90: int
    seasonality_coefficient: float
    trend_coefficient: float
    warnings: list[str] = Field(default_factory=list)
    mock_mode: bool = True


class StockForecastReport(BaseModel):
    items: list[StockForecastItem] = Field(default_factory=list)
    self_check: SelfCheckResult
    mock_mode: bool = True


class ForecastABCReport(BaseModel):
    abc: ABCAnalysisReport
    stock_forecast: StockForecastReport
    seasonality: list[SeasonalityResult] = Field(default_factory=list)
    self_check: SelfCheckResult
    recommendation: str
    mock_mode: bool = True


class MarketplaceSalesProvider(Protocol):
    def fetch_sales_by_sku(self, date_from: str, date_to: str) -> list[MarketplaceSkuSnapshot]: ...

    def fetch_orders_by_sku(self, date_from: str, date_to: str) -> list[dict]: ...

    def fetch_stocks_by_warehouse(self) -> list[MarketplaceSkuSnapshot]: ...

    def fetch_stock_movements(self) -> list[dict]: ...

    def fetch_product_mapping(self) -> dict[str, dict]: ...

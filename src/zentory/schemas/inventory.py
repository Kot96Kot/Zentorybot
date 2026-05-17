from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class InventoryStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCESS = "excess"
    SLOW_MOVER = "slow_mover"


class InventoryPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WarehouseStock(BaseModel):
    warehouse: str
    region: str
    stock: int
    is_key_warehouse: bool = False
    in_transit: int = 0


class InventorySkuInput(BaseModel):
    sku: str
    total_stock: int
    warehouse_stocks: list[WarehouseStock] = Field(default_factory=list)
    sales_7d: int
    sales_14d: int
    sales_30d: int
    average_daily_sales: float
    coverage_days: float
    warehouse: str
    region: str
    transit: int
    supply_plan: int
    minimum_stock: int
    desired_stock_days: int
    recent_daily_sales: list[int] = Field(default_factory=list)
    is_advertised: bool = False
    days_without_movement: int = 0
    mock: bool = True


class ReplenishmentRecommendation(BaseModel):
    recommendation_type: str
    title: str
    description: str
    target_warehouse: str | None = None
    target_region: str | None = None
    suggested_quantity: int = 0
    priority: InventoryPriority = InventoryPriority.LOW
    requires_approval: bool = True
    mock: bool = True


class InventorySkuReport(BaseModel):
    sku: str
    status: InventoryStatus
    priority: InventoryPriority
    total_stock: int
    average_daily_sales: float
    coverage_days: float
    stockout_date: date | None = None
    out_of_stock_risk: bool = False
    excess_stock: bool = False
    slow_mover: bool = False
    telegram_alert: str | None = None
    recommendations: list[ReplenishmentRecommendation] = Field(default_factory=list)
    warehouse_stocks: list[WarehouseStock] = Field(default_factory=list)
    alerts_for_ads_agent: list[str] = Field(default_factory=list)
    mock: bool = True


class InventorySummary(BaseModel):
    out_of_stock_risks: list[InventorySkuReport] = Field(default_factory=list)
    excess_skus: list[InventorySkuReport] = Field(default_factory=list)
    slow_movers: list[InventorySkuReport] = Field(default_factory=list)
    reports: list[InventorySkuReport] = Field(default_factory=list)
    mock: bool = True

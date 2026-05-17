from enum import StrEnum

from pydantic import BaseModel, Field


class SupplyPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SupplyPlannerInput(BaseModel):
    sku: str
    warehouse: str
    region: str
    stock_qty: int
    sales_qty_7d: int
    sales_qty_30d: int
    avg_daily_sales: float
    lead_time_days: int
    target_coverage_days: int
    localization_index: float
    logistics_cost: float
    available_for_supply: int
    is_advertised: bool = False
    sales_qty_prev_30d: int | None = None
    sales_qty_prev_prev_30d: int | None = None
    mock_mode: bool = True

    @property
    def coverage_days(self) -> float | None:
        if self.avg_daily_sales <= 0:
            return None
        return round(self.stock_qty / self.avg_daily_sales, 2)


class SupplyRecommendation(BaseModel):
    sku: str
    warehouse: str
    region: str
    recommended_supply_qty: int
    target_warehouse: str
    priority: SupplyPriority
    reason: str
    expected_coverage_days: float | None
    localization_impact: float
    replenishment_cost: float
    warning_list: list[str] = Field(default_factory=list)
    approval_required: bool = False
    mock_mode: bool = True


class WarehouseLocalization(BaseModel):
    warehouse: str
    region: str
    localization_index: float
    logistics_cost: float
    target_warehouse: str
    localization_impact: float
    redistribution_recommended: bool
    reason: str
    mock_mode: bool = True


class SupplyPlannerReport(BaseModel):
    risks: list[SupplyRecommendation] = Field(default_factory=list)
    replenishment: list[SupplyRecommendation] = Field(default_factory=list)
    warehouses: list[WarehouseLocalization] = Field(default_factory=list)
    recommendations: list[SupplyRecommendation] = Field(default_factory=list)
    ads_alerts: list[dict[str, str]] = Field(default_factory=list)
    mock_mode: bool = True

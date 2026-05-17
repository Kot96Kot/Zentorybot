from enum import StrEnum

from pydantic import BaseModel, Field

from zentory.core.enums import RiskLevel


class PromoDecision(StrEnum):
    ALLOW = "allow"
    ALLOW_WITH_APPROVAL = "allow_with_approval"
    REJECT = "reject"


class PromoSkuInput(BaseModel):
    sku: str
    current_price: float
    promo_price: float
    discount_percent: float
    commission_percent: float
    logistics_cost: float
    cost_price: float
    advertising_cost_per_unit: float
    tax_percent: float
    minimum_margin_percent: float
    current_sales: int
    stock: int
    forecast_sales_growth_percent: float
    promo_duration_days: int
    acquiring_percent: float = 0.02
    storage_cost_per_unit: float = 0
    penalties_per_unit: float = 0
    return_logistics_per_unit: float = 0
    is_slow_mover: bool = False
    mock: bool = True


class UnitProfitBreakdown(BaseModel):
    revenue: float
    commission: float
    logistics: float
    acquiring: float
    advertising: float
    cost_price: float
    storage: float
    penalties: float
    return_logistics: float
    taxes: float
    profit: float
    margin_percent: float
    mandatory_costs: float
    mock: bool = True


class PromoRecommendation(BaseModel):
    decision: PromoDecision
    title: str
    description: str
    requires_approval: bool = True
    risk_level: RiskLevel
    mock: bool = True


class PromoAnalysisReport(BaseModel):
    sku: str
    can_participate: bool
    minimum_price: float
    forecast_margin_percent: float
    forecast_profit: float
    forecast_units: int
    forecast_revenue: float
    risk_level: RiskLevel
    recommendation: PromoRecommendation
    dangerous: bool = False
    warnings: list[str] = Field(default_factory=list)
    profit_breakdown: UnitProfitBreakdown
    mock: bool = True


class PromoSummary(BaseModel):
    reports: list[PromoAnalysisReport] = Field(default_factory=list)
    dangerous_skus: list[PromoAnalysisReport] = Field(default_factory=list)
    mock: bool = True

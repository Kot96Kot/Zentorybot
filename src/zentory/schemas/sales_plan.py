from enum import StrEnum

from pydantic import BaseModel, Field, computed_field


class SalesPlanStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class MarketplaceArticle(BaseModel):
    marketplace: str
    article: str


class SalesPlanInput(BaseModel):
    sku: str
    marketplace_articles: list[MarketplaceArticle] = Field(default_factory=list)
    current_sales: int = 0
    sales_7d: int = 0
    sales_14d: int = 0
    sales_30d: int = 0
    stock: int = 0
    average_price: float = 0
    target_revenue: float = 0
    target_margin: float = 0
    ad_spend: float = 0
    impressions: int = 0
    seasonal_coefficient: float = 1.0
    drr_limit: float = 0.18

    @computed_field
    @property
    def fact_revenue(self) -> float:
        return self.current_sales * self.average_price


class SalesPlanReport(BaseModel):
    sku: str
    day_plan: int
    week_plan: int
    month_plan: int
    fact: int
    deviation_percent: float
    status: SalesPlanStatus
    recommendations: list[str] = Field(default_factory=list)
    alerts: list[str] = Field(default_factory=list)
    tasks: list[str] = Field(default_factory=list)
    stock_days_left: float | None = None
    drr: float | None = None
    mock: bool = True

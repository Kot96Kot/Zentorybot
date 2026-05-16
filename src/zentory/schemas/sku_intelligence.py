from typing import Any

from pydantic import BaseModel, Field

from zentory.core.enums import ApprovalMode, RiskLevel


class MarketplaceArticles(BaseModel):
    wildberries: str
    ozon: str
    yandex_market: str


class SalesSnapshot(BaseModel):
    day_units: int
    week_units: int
    month_units: int
    revenue: float
    margin_percent: float


class StockSnapshot(BaseModel):
    stock_units: int
    coverage_days: int


class AdvertisingSnapshot(BaseModel):
    drr_percent: float
    ctr_percent: float
    clicks: int
    carts: int
    orders: int
    cart_conversion_percent: float
    order_conversion_percent: float


class ReviewSnapshot(BaseModel):
    rating: float
    reviews_count: int
    latest_reviews: list[str] = Field(default_factory=list)


class CompetitorSnapshot(BaseModel):
    sku: str
    name: str
    price: float
    rating: float
    search_position: int


class ApprovalAction(BaseModel):
    action_id: str
    title: str
    risk_level: RiskLevel
    approval_mode: ApprovalMode
    rollback_available: bool = True
    command: str


class SKUIntelligenceCard(BaseModel):
    sku: str
    articles: MarketplaceArticles
    name: str
    sales: SalesSnapshot
    stock: StockSnapshot
    advertising: AdvertisingSnapshot
    reviews: ReviewSnapshot
    search_position: int
    competitor: CompetitorSnapshot
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    approval_actions: list[ApprovalAction] = Field(default_factory=list)
    mock: bool = True

    def to_summary(self) -> dict[str, Any]:
        return {
            "sku": self.sku,
            "name": self.name,
            "risk": "critical" if self.risks else "ok",
            "stock_days": self.stock.coverage_days,
            "sales_delta": f"{self.sales.week_units} шт/нед.",
            "ads": f"ДРР {self.advertising.drr_percent}% · CTR {self.advertising.ctr_percent}%",
            "recommendation": self.recommendations[0] if self.recommendations else "наблюдать",
        }

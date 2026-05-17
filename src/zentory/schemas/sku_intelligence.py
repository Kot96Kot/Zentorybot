from typing import Any

from pydantic import BaseModel, Field

from zentory.core.enums import ApprovalMode, RiskLevel


class MarketplaceArticles(BaseModel):
    wildberries: str
    ozon: str
    yandex_market: str


class SKUBasicInfo(BaseModel):
    sku: str
    nm_id: int
    vendor_code: str
    marketplace: str
    product_name: str
    category: str
    brand: str


class SKUSalesMetrics(BaseModel):
    sales_qty_day: int
    sales_qty_7d: int
    sales_qty_30d: int
    revenue_day: float
    revenue_30d: float
    avg_price: float
    buyout_percent: float
    margin_percent: float

    @property
    def day_units(self) -> int:
        return self.sales_qty_day

    @property
    def week_units(self) -> int:
        return self.sales_qty_7d

    @property
    def month_units(self) -> int:
        return self.sales_qty_30d

    @property
    def revenue(self) -> float:
        return self.revenue_30d


class SKUStockMetrics(BaseModel):
    total_stock: int
    stock_by_warehouse: dict[str, int]
    days_of_coverage: int
    stock_status: str

    @property
    def stock_units(self) -> int:
        return self.total_stock

    @property
    def coverage_days(self) -> int:
        return self.days_of_coverage


class SKUAdvertisingMetrics(BaseModel):
    impressions: int
    ctr: float
    clicks: int
    spend: float
    drr: float
    orders_from_ads: int
    campaign_status: str
    carts: int

    @property
    def drr_percent(self) -> float:
        return self.drr

    @property
    def ctr_percent(self) -> float:
        return self.ctr

    @property
    def orders(self) -> int:
        return self.orders_from_ads


class SKUConversionMetrics(BaseModel):
    cart_conversion: float
    order_conversion: float
    click_to_order: float

    @property
    def cart_conversion_percent(self) -> float:
        return self.cart_conversion

    @property
    def order_conversion_percent(self) -> float:
        return self.order_conversion


class SKUReputationMetrics(BaseModel):
    rating: float
    reviews_count: int
    negative_reviews_count: int
    unanswered_questions: int
    latest_reviews: list[str] = Field(default_factory=list)


class SKUCompetitorComparison(BaseModel):
    competitor_sku: str
    competitor_price: float
    competitor_rating: float
    where_we_are_stronger: list[str] = Field(default_factory=list)
    where_we_are_weaker: list[str] = Field(default_factory=list)

    @property
    def sku(self) -> str:
        return self.competitor_sku

    @property
    def name(self) -> str:
        return "Mock конкурент"

    @property
    def price(self) -> float:
        return self.competitor_price

    @property
    def rating(self) -> float:
        return self.competitor_rating

    @property
    def search_position(self) -> int:
        return 9


class SKURiskFlags(BaseModel):
    low_stock: bool
    high_drr: bool
    low_ctr: bool
    low_margin: bool
    rating_risk: bool
    out_of_stock: bool

    def active_labels(self) -> list[str]:
        labels = {
            "low_stock": "Остаток ниже safety-порога",
            "high_drr": "ДРР выше целевого уровня",
            "low_ctr": "CTR ниже нормы",
            "low_margin": "Маржа ниже целевого уровня",
            "rating_risk": "Рейтинг несет риск просадки конверсии",
            "out_of_stock": "Есть риск out-of-stock",
        }
        return [label for key, label in labels.items() if getattr(self, key)]


class SKURecommendation(BaseModel):
    title: str
    reason: str
    expected_effect: str
    risk_level: RiskLevel
    approval_required: bool


class ApprovalAction(BaseModel):
    action_id: str
    title: str
    risk_level: RiskLevel
    approval_mode: ApprovalMode
    rollback_available: bool = True
    command: str


class SKUIntelligenceCard(BaseModel):
    basic: SKUBasicInfo
    sales: SKUSalesMetrics
    stock: SKUStockMetrics
    advertising: SKUAdvertisingMetrics
    conversion: SKUConversionMetrics
    reputation: SKUReputationMetrics
    competitor: SKUCompetitorComparison
    risks: SKURiskFlags
    recommendations: list[SKURecommendation] = Field(default_factory=list)
    mock: bool = True

    @property
    def sku(self) -> str:
        return self.basic.sku

    @property
    def nm_id(self) -> int:
        return self.basic.nm_id

    @property
    def vendor_code(self) -> str:
        return self.basic.vendor_code

    @property
    def marketplace(self) -> str:
        return self.basic.marketplace

    @property
    def product_name(self) -> str:
        return self.basic.product_name

    @property
    def category(self) -> str:
        return self.basic.category

    @property
    def brand(self) -> str:
        return self.basic.brand

    @property
    def articles(self) -> MarketplaceArticles:
        return MarketplaceArticles(
            wildberries=f"WB-ART-{self.sku}",
            ozon=f"OZON-ART-{self.sku}",
            yandex_market=f"YM-ART-{self.sku}",
        )

    @property
    def name(self) -> str:
        return self.product_name

    @property
    def reviews(self) -> SKUReputationMetrics:
        return self.reputation

    @property
    def search_position(self) -> int:
        return 18

    @property
    def strengths(self) -> list[str]:
        return self.competitor.where_we_are_stronger

    @property
    def weaknesses(self) -> list[str]:
        return self.competitor.where_we_are_weaker


    @property
    def approval_actions(self) -> list[ApprovalAction]:
        return [
            ApprovalAction(
                action_id=f"{self.sku}-{index}",
                title=item.title,
                risk_level=item.risk_level,
                approval_mode=ApprovalMode.HARD_APPROVAL
                if item.approval_required
                else ApprovalMode.NONE,
                rollback_available=True,
                command=f"/approve {self.sku}-{index}",
            )
            for index, item in enumerate(self.recommendations, start=1)
        ]

    @property
    def active_risks(self) -> list[str]:
        return self.risks.active_labels()

    def to_summary(self) -> dict[str, Any]:
        first_recommendation = (
            self.recommendations[0].title if self.recommendations else "наблюдать"
        )
        return {
            "sku": self.sku,
            "name": self.product_name,
            "risk": "critical" if self.active_risks else "ok",
            "stock_days": self.stock.days_of_coverage,
            "sales_delta": f"{self.sales.sales_qty_7d} шт/нед.",
            "ads": f"ДРР {self.advertising.drr}% · CTR {self.advertising.ctr}%",
            "recommendation": first_recommendation,
        }

# Backward-compatible names for existing imports while the public SKU card contract
# uses the explicit SKU* block models above.
SalesSnapshot = SKUSalesMetrics
StockSnapshot = SKUStockMetrics
AdvertisingSnapshot = SKUAdvertisingMetrics
ReviewSnapshot = SKUReputationMetrics
CompetitorSnapshot = SKUCompetitorComparison

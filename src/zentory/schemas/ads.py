from enum import StrEnum

from pydantic import BaseModel, Field


class AdsReportStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class AdsRecommendationType(StrEnum):
    LOWER_BID = "lower_bid"
    PAUSE_CAMPAIGN = "pause_campaign"
    TEST_MAIN_PHOTO = "test_main_photo"
    CHECK_PRICE_OFFER = "check_price_offer"
    FORBID_ADS_SCALE = "forbid_ads_scale"
    RAISE_BID_CAREFULLY = "raise_bid_carefully"
    CRITICAL_SPEND_ALERT = "critical_spend_alert"
    KEEP_MONITORING = "keep_monitoring"


class AdsCampaignMetrics(BaseModel):
    campaign_id: str
    sku: str
    marketplace: str
    campaign_name: str
    impressions: int
    ctr: float
    clicks: int
    pricing_model: str = "CPC"
    cpc: float | None = None
    cpm: float | None = None
    spend: float
    orders: int
    revenue: float
    cart_conversion: float
    order_conversion: float
    average_position: float
    bid: float
    sku_stock: int
    sku_margin: float
    drr_limit: float = 0.18
    ctr_limit: float = 0.02
    daily_spend_limit: float = 10_000
    low_orders_threshold: int = 2
    mock: bool = True


class AdsRecommendation(BaseModel):
    recommendation_type: AdsRecommendationType
    title: str
    description: str
    suggested_bid: float | None = None
    can_execute_automatically: bool = False
    requires_approval: bool = True


class AdsCampaignReport(BaseModel):
    campaign_id: str
    sku: str
    marketplace: str
    campaign_name: str
    impressions: int
    ctr: float
    clicks: int
    cpc: float | None = None
    cpm: float | None = None
    spend: float
    orders: int
    revenue: float
    drr: float
    cart_conversion: float
    order_conversion: float
    average_position: float
    bid: float
    sku_stock: int
    sku_margin: float
    stock_days_left: float
    status: AdsReportStatus
    recommendations: list[AdsRecommendation] = Field(default_factory=list)
    alerts: list[str] = Field(default_factory=list)
    mock: bool = True

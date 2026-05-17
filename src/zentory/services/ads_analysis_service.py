from zentory.schemas.ads import (
    AdsCampaignMetrics,
    AdsCampaignReport,
    AdsRecommendation,
    AdsRecommendationType,
    AdsReportStatus,
)
from zentory.services.bid_recommendation_service import BidRecommendationService


class AdsAnalysisService:
    def __init__(self, bid_service: BidRecommendationService | None = None) -> None:
        self.bid_service = bid_service or BidRecommendationService()

    def build_mock_campaigns(
        self, *, sku: str | None = None, campaign_id: str | None = None
    ) -> list[AdsCampaignMetrics]:
        campaigns = [
            AdsCampaignMetrics(
                campaign_id="WB-ADS-101",
                sku="ZNT-WB-001",
                marketplace="wildberries",
                campaign_name="Поиск / вакууматоры",
                impressions=48_000,
                ctr=0.031,
                clicks=1488,
                cpc=18.5,
                spend=27_528,
                orders=0,
                revenue=0,
                cart_conversion=0.12,
                order_conversion=0,
                average_position=5.4,
                bid=62,
                sku_stock=420,
                sku_margin=0.31,
                drr_limit=0.18,
                daily_spend_limit=20_000,
            ),
            AdsCampaignMetrics(
                campaign_id="OZ-ADS-202",
                sku="ZNT-OZON-002",
                marketplace="ozon",
                campaign_name="Карточка / аксессуары",
                impressions=22_400,
                ctr=0.009,
                clicks=202,
                cpc=24.0,
                spend=4_848,
                orders=3,
                revenue=18_900,
                cart_conversion=0.04,
                order_conversion=0.014,
                average_position=9.8,
                bid=45,
                sku_stock=18,
                sku_margin=0.24,
                drr_limit=0.2,
                daily_spend_limit=8_000,
            ),
            AdsCampaignMetrics(
                campaign_id="YM-ADS-303",
                sku="ZNT-YM-003",
                marketplace="yandex_market",
                campaign_name="Категория / хиты",
                impressions=31_000,
                ctr=0.045,
                clicks=1395,
                cpc=11.2,
                spend=15_624,
                orders=28,
                revenue=143_500,
                cart_conversion=0.22,
                order_conversion=0.02,
                average_position=3.1,
                bid=38,
                sku_stock=62,
                sku_margin=0.36,
                drr_limit=0.18,
                daily_spend_limit=25_000,
            ),
        ]
        if sku is not None:
            campaigns = [campaign for campaign in campaigns if campaign.sku == sku]
        if campaign_id is not None:
            campaigns = [campaign for campaign in campaigns if campaign.campaign_id == campaign_id]
        return campaigns

    def analyze(self, metrics: AdsCampaignMetrics) -> AdsCampaignReport:
        drr = self._drr(metrics)
        stock_days_left = self._stock_days_left(metrics)
        recommendations: list[AdsRecommendation] = []
        alerts: list[str] = []

        if metrics.spend > metrics.daily_spend_limit:
            alerts.append("Расход за день выше лимита: отправить critical alert менеджеру.")
            recommendations.append(
                AdsRecommendation(
                    recommendation_type=AdsRecommendationType.CRITICAL_SPEND_ALERT,
                    title="Critical alert по дневному расходу",
                    description="Расход за день превысил лимит, автодействия запрещены.",
                )
            )
        if drr > metrics.drr_limit and metrics.orders == 0:
            recommendations.append(self.bid_service.pause_campaign(metrics))
        elif drr > metrics.drr_limit and metrics.orders <= metrics.low_orders_threshold:
            recommendations.append(self.bid_service.lower_bid(metrics))
        if metrics.ctr < metrics.ctr_limit:
            recommendations.append(
                AdsRecommendation(
                    recommendation_type=AdsRecommendationType.TEST_MAIN_PHOTO,
                    title="Создать тест главного фото",
                    description=(
                        "CTR ниже лимита: нужна гипотеза по главному фото и первому экрану."
                    ),
                )
            )
        if metrics.cart_conversion >= 0.1 and metrics.order_conversion < 0.02:
            recommendations.append(
                AdsRecommendation(
                    recommendation_type=AdsRecommendationType.CHECK_PRICE_OFFER,
                    title="Проверить цену и оффер",
                    description=(
                        "Корзина хорошая, но заказ слабый: проверить цену, доставку и оффер."
                    ),
                )
            )
        if stock_days_left < 7:
            alerts.append("Остатка SKU меньше 7 дней: усиление рекламы запрещено.")
            recommendations.append(
                AdsRecommendation(
                    recommendation_type=AdsRecommendationType.FORBID_ADS_SCALE,
                    title="Запретить усиление рекламы",
                    description="Остаток меньше 7 дней, нельзя повышать ставку или бюджет.",
                )
            )
        if self._is_profitable(metrics, drr) and stock_days_left >= 7:
            recommendations.append(self.bid_service.raise_bid_carefully(metrics))
        if not recommendations:
            recommendations.append(
                AdsRecommendation(
                    recommendation_type=AdsRecommendationType.KEEP_MONITORING,
                    title="Продолжать мониторинг",
                    description="Критичных проблем не найдено, оставить кампанию под наблюдением.",
                    requires_approval=False,
                )
            )

        return AdsCampaignReport(
            campaign_id=metrics.campaign_id,
            sku=metrics.sku,
            marketplace=metrics.marketplace,
            campaign_name=metrics.campaign_name,
            impressions=metrics.impressions,
            ctr=metrics.ctr,
            clicks=metrics.clicks,
            cpc=metrics.cpc,
            cpm=metrics.cpm,
            spend=metrics.spend,
            orders=metrics.orders,
            revenue=metrics.revenue,
            drr=round(drr, 4),
            cart_conversion=metrics.cart_conversion,
            order_conversion=metrics.order_conversion,
            average_position=metrics.average_position,
            bid=metrics.bid,
            sku_stock=metrics.sku_stock,
            sku_margin=metrics.sku_margin,
            stock_days_left=round(stock_days_left, 1),
            status=self._status(alerts, recommendations),
            recommendations=recommendations,
            alerts=alerts,
            mock=True,
        )

    def analyze_many(
        self, *, sku: str | None = None, campaign_id: str | None = None
    ) -> list[AdsCampaignReport]:
        return [
            self.analyze(campaign)
            for campaign in self.build_mock_campaigns(sku=sku, campaign_id=campaign_id)
        ]

    @staticmethod
    def _drr(metrics: AdsCampaignMetrics) -> float:
        if metrics.revenue <= 0:
            return 1.0 if metrics.spend > 0 else 0.0
        return metrics.spend / metrics.revenue

    @staticmethod
    def _stock_days_left(metrics: AdsCampaignMetrics) -> float:
        daily_sales = max(metrics.orders / 7, 1)
        return metrics.sku_stock / daily_sales

    @staticmethod
    def _is_profitable(metrics: AdsCampaignMetrics, drr: float) -> bool:
        return metrics.orders >= 5 and drr < metrics.drr_limit and metrics.sku_margin > drr

    @staticmethod
    def _status(alerts: list[str], recommendations: list[AdsRecommendation]) -> AdsReportStatus:
        if alerts or any(
            recommendation.recommendation_type
            in {AdsRecommendationType.PAUSE_CAMPAIGN, AdsRecommendationType.CRITICAL_SPEND_ALERT}
            for recommendation in recommendations
        ):
            return AdsReportStatus.CRITICAL
        if any(
            recommendation.recommendation_type != AdsRecommendationType.KEEP_MONITORING
            for recommendation in recommendations
        ):
            return AdsReportStatus.WARNING
        return AdsReportStatus.OK

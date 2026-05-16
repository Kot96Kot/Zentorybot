from zentory.schemas.ads import AdsCampaignMetrics, AdsRecommendation, AdsRecommendationType


class BidRecommendationService:
    def lower_bid(self, metrics: AdsCampaignMetrics) -> AdsRecommendation:
        suggested_bid = round(metrics.bid * 0.85, 2)
        return AdsRecommendation(
            recommendation_type=AdsRecommendationType.LOWER_BID,
            title="Снизить ставку",
            description=(
                "ДРР выше лимита, а заказов мало: рекомендуется снизить ставку "
                f"с {metrics.bid} до {suggested_bid}."
            ),
            suggested_bid=suggested_bid,
        )

    def pause_campaign(self, metrics: AdsCampaignMetrics) -> AdsRecommendation:
        return AdsRecommendation(
            recommendation_type=AdsRecommendationType.PAUSE_CAMPAIGN,
            title="Поставить кампанию на паузу",
            description="ДРР высокий и заказов нет: рекомендуется пауза до проверки экономики.",
            suggested_bid=0,
        )

    def raise_bid_carefully(self, metrics: AdsCampaignMetrics) -> AdsRecommendation:
        suggested_bid = round(metrics.bid * 1.1, 2)
        return AdsRecommendation(
            recommendation_type=AdsRecommendationType.RAISE_BID_CAREFULLY,
            title="Аккуратно поднять ставку",
            description=(
                "Кампания прибыльная: можно протестировать плавное повышение ставки "
                f"с {metrics.bid} до {suggested_bid}."
            ),
            suggested_bid=suggested_bid,
        )

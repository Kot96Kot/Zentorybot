from collections import Counter

from zentory.schemas.platform_modules import (
    ABCClass,
    ForecastABCItem,
    ForecastABCReport,
    Marketplace,
)


class ForecastABCService:
    def build_report(self, horizon_days: int = 14) -> ForecastABCReport:
        items = [
            ForecastABCItem(
                sku="WB-MOCK-1",
                marketplace=Marketplace.WILDBERRIES,
                revenue_share_percent=42.5,
                units_forecast_14d=260,
                abc_class=ABCClass.A,
                stockout_risk=True,
                recommended_action="Пополнить до усиления рекламы и сохранить safety buffer.",
            ),
            ForecastABCItem(
                sku="OZON-MOCK-2",
                marketplace=Marketplace.OZON,
                revenue_share_percent=18.4,
                units_forecast_14d=96,
                abc_class=ABCClass.B,
                stockout_risk=False,
                recommended_action="Держать текущие ставки, проверить карточку после теста CTR.",
            ),
            ForecastABCItem(
                sku="ZNT-YM-003",
                marketplace=Marketplace.YANDEX_MARKET,
                revenue_share_percent=4.1,
                units_forecast_14d=8,
                abc_class=ABCClass.C,
                stockout_risk=False,
                recommended_action="Не закупать дополнительно до подтверждения спроса.",
            ),
        ]
        summary = Counter(item.abc_class.value for item in items)
        return ForecastABCReport(horizon_days=horizon_days, items=items, summary=dict(summary))

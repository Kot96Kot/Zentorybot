from zentory.schemas.sales_plan import (
    MarketplaceArticle,
    SalesPlanInput,
    SalesPlanReport,
    SalesPlanStatus,
)


class SalesPlanService:
    def build_mock_inputs(self, sku: str | None = None) -> list[SalesPlanInput]:
        items = [
            SalesPlanInput(
                sku="ZNT-WB-001",
                marketplace_articles=[
                    MarketplaceArticle(marketplace="wildberries", article="WB-10001")
                ],
                current_sales=26,
                sales_7d=210,
                sales_14d=405,
                sales_30d=820,
                stock=560,
                average_price=1490,
                target_revenue=1_350_000,
                target_margin=0.32,
                ad_spend=96_000,
                impressions=42_000,
                seasonal_coefficient=1.08,
                drr_limit=0.18,
            ),
            SalesPlanInput(
                sku="ZNT-OZON-002",
                marketplace_articles=[MarketplaceArticle(marketplace="ozon", article="OZ-20002")],
                current_sales=11,
                sales_7d=126,
                sales_14d=260,
                sales_30d=610,
                stock=120,
                average_price=2190,
                target_revenue=1_900_000,
                target_margin=0.28,
                ad_spend=190_000,
                impressions=31_500,
                seasonal_coefficient=1.0,
                drr_limit=0.16,
            ),
            SalesPlanInput(
                sku="ZNT-YM-003",
                marketplace_articles=[
                    MarketplaceArticle(marketplace="yandex_market", article="YM-30003")
                ],
                current_sales=0,
                sales_7d=18,
                sales_14d=46,
                sales_30d=120,
                stock=38,
                average_price=3290,
                target_revenue=680_000,
                target_margin=0.35,
                ad_spend=32_000,
                impressions=8_900,
                seasonal_coefficient=0.95,
                drr_limit=0.15,
            ),
        ]
        if sku is None:
            return items
        return [item for item in items if item.sku == sku]

    def calculate_report(self, data: SalesPlanInput) -> SalesPlanReport:
        day_plan = self._day_plan(data)
        week_plan = day_plan * 7
        month_plan = day_plan * 30
        deviation_percent = self._deviation_percent(data.current_sales, day_plan)
        stock_days_left = self._stock_days_left(data.stock, day_plan)
        drr = self._drr(data.ad_spend, data.target_revenue)
        status = self._status(deviation_percent)
        alerts: list[str] = []
        tasks: list[str] = []
        recommendations: list[str] = []

        if status == SalesPlanStatus.WARNING:
            recommendations.append(
                "Факт ниже плана больше чем на 15%: проверить трафик и конверсию."
            )
        if status == SalesPlanStatus.CRITICAL:
            recommendations.append(
                "Факт ниже плана больше чем на 30%: поднять приоритет SKU на сегодня."
            )
        if stock_days_left < 14:
            alerts.append("Остатка меньше чем на 14 дней: создать alert по закупке или подсорту.")
        if drr > data.drr_limit:
            alerts.append("ДРР выше лимита: проверить рекламные ставки и неэффективные кампании.")
        if data.current_sales == 0 and data.impressions > 0:
            tasks.append("Заказов нет, но показы есть: создать задачу на анализ карточки.")
        if not recommendations:
            recommendations.append("План выполняется: продолжать мониторинг продаж и остатков.")

        return SalesPlanReport(
            sku=data.sku,
            day_plan=day_plan,
            week_plan=week_plan,
            month_plan=month_plan,
            fact=data.current_sales,
            deviation_percent=round(deviation_percent, 2),
            status=status,
            recommendations=recommendations,
            alerts=alerts,
            tasks=tasks,
            stock_days_left=round(stock_days_left, 1),
            drr=round(drr, 4),
            mock=True,
        )

    def calculate_reports(self, sku: str | None = None) -> list[SalesPlanReport]:
        return [self.calculate_report(item) for item in self.build_mock_inputs(sku)]

    def _day_plan(self, data: SalesPlanInput) -> int:
        target_units_per_day = data.target_revenue / max(data.average_price, 1) / 30
        historical_daily_sales = max(data.sales_7d / 7, data.sales_14d / 14, data.sales_30d / 30)
        seasonal_plan = historical_daily_sales * data.seasonal_coefficient
        return max(1, round(max(target_units_per_day, seasonal_plan)))

    @staticmethod
    def _deviation_percent(fact: int, day_plan: int) -> float:
        if day_plan <= 0:
            return 0
        return (fact - day_plan) / day_plan * 100

    @staticmethod
    def _stock_days_left(stock: int, day_plan: int) -> float:
        return stock / max(day_plan, 1)

    @staticmethod
    def _drr(ad_spend: float, target_revenue: float) -> float:
        return ad_spend / max(target_revenue, 1)

    @staticmethod
    def _status(deviation_percent: float) -> SalesPlanStatus:
        if deviation_percent < -30:
            return SalesPlanStatus.CRITICAL
        if deviation_percent < -15:
            return SalesPlanStatus.WARNING
        return SalesPlanStatus.OK

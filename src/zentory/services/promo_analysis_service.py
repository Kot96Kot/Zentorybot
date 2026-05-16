from math import ceil

from zentory.core.enums import RiskLevel
from zentory.schemas.promo import (
    PromoAnalysisReport,
    PromoDecision,
    PromoRecommendation,
    PromoSkuInput,
    PromoSummary,
)
from zentory.services.unit_profit_service import UnitProfitService


class PromoAnalysisService:
    def __init__(self, profit_service: UnitProfitService | None = None) -> None:
        self.profit_service = profit_service or UnitProfitService()

    def build_mock_items(self, sku: str | None = None) -> list[PromoSkuInput]:
        items = [
            PromoSkuInput(
                sku="ZNT-WB-001",
                current_price=1990,
                promo_price=1690,
                discount_percent=0.15,
                commission_percent=0.18,
                logistics_cost=130,
                cost_price=820,
                advertising_cost_per_unit=120,
                tax_percent=0.06,
                minimum_margin_percent=0.18,
                current_sales=12,
                stock=320,
                forecast_sales_growth_percent=0.35,
                promo_duration_days=10,
                storage_cost_per_unit=12,
                return_logistics_per_unit=25,
            ),
            PromoSkuInput(
                sku="ZNT-OZON-002",
                current_price=2190,
                promo_price=1190,
                discount_percent=0.46,
                commission_percent=0.2,
                logistics_cost=180,
                cost_price=980,
                advertising_cost_per_unit=160,
                tax_percent=0.06,
                minimum_margin_percent=0.16,
                current_sales=9,
                stock=80,
                forecast_sales_growth_percent=0.9,
                promo_duration_days=14,
                storage_cost_per_unit=18,
                return_logistics_per_unit=35,
            ),
            PromoSkuInput(
                sku="ZNT-YM-003",
                current_price=3290,
                promo_price=2990,
                discount_percent=0.09,
                commission_percent=0.16,
                logistics_cost=210,
                cost_price=1900,
                advertising_cost_per_unit=60,
                tax_percent=0.06,
                minimum_margin_percent=0.2,
                current_sales=1,
                stock=600,
                forecast_sales_growth_percent=0.55,
                promo_duration_days=21,
                storage_cost_per_unit=30,
                return_logistics_per_unit=50,
                is_slow_mover=True,
            ),
        ]
        if sku is None:
            return items
        return [item for item in items if item.sku == sku]

    def analyze_item(self, item: PromoSkuInput) -> PromoAnalysisReport:
        breakdown = self.profit_service.calculate(item)
        minimum_price = self.profit_service.minimum_price(item)
        forecast_units = self._forecast_units(item)
        forecast_revenue = item.promo_price * forecast_units
        forecast_profit = breakdown.profit * forecast_units
        stock_days = self._stock_days(item, forecast_units)
        warnings: list[str] = []
        decision = PromoDecision.ALLOW
        risk = RiskLevel.MEDIUM
        title = "Можно участвовать в акции только после approval"
        description = "Акция сохраняет минимальную маржу, но применение требует подтверждения."

        if stock_days < 14:
            warnings.append("Остатка меньше чем на 14 дней: нужен warning перед участием.")
        if item.promo_price < breakdown.mandatory_costs:
            decision = PromoDecision.REJECT
            risk = RiskLevel.CRITICAL
            title = "Запретить участие: цена ниже обязательных расходов"
            description = "Цена акции ниже себестоимости и обязательных расходов."
        elif breakdown.margin_percent < item.minimum_margin_percent:
            if item.is_slow_mover and stock_days >= item.promo_duration_days:
                decision = PromoDecision.ALLOW_WITH_APPROVAL
                risk = RiskLevel.HIGH
                title = "Slow mover: разрешить низкую маржу только с approval"
                description = "Акция помогает распродать slow mover, но маржа ниже цели."
            else:
                decision = PromoDecision.REJECT
                risk = RiskLevel.HIGH
                title = "Запретить участие: маржа ниже минимальной"
                description = "Акция дает рост оборота, но убивает прибыль или маржинальность."
        elif forecast_revenue > item.current_price * item.current_sales * item.promo_duration_days:
            risk = RiskLevel.MEDIUM
            description = "Акция может дать рост оборота без нарушения минимальной маржи."

        dangerous = risk in {RiskLevel.HIGH, RiskLevel.CRITICAL} or decision == PromoDecision.REJECT
        recommendation = PromoRecommendation(
            decision=decision,
            title=title,
            description=description,
            requires_approval=True,
            risk_level=risk,
            mock=True,
        )
        return PromoAnalysisReport(
            sku=item.sku,
            can_participate=decision != PromoDecision.REJECT,
            minimum_price=minimum_price,
            forecast_margin_percent=breakdown.margin_percent,
            forecast_profit=round(forecast_profit, 2),
            forecast_units=forecast_units,
            forecast_revenue=round(forecast_revenue, 2),
            risk_level=risk,
            recommendation=recommendation,
            dangerous=dangerous,
            warnings=warnings,
            profit_breakdown=breakdown,
            mock=True,
        )

    def analyze(self, sku: str | None = None) -> PromoSummary:
        reports = [self.analyze_item(item) for item in self.build_mock_items(sku)]
        return PromoSummary(
            reports=reports,
            dangerous_skus=[report for report in reports if report.dangerous],
            mock=True,
        )

    @staticmethod
    def _forecast_units(item: PromoSkuInput) -> int:
        base_units = item.current_sales * item.promo_duration_days
        return max(1, ceil(base_units * (1 + item.forecast_sales_growth_percent)))

    @staticmethod
    def _stock_days(item: PromoSkuInput, forecast_units: int) -> float:
        forecast_daily_sales = forecast_units / max(item.promo_duration_days, 1)
        return item.stock / max(forecast_daily_sales, 1)

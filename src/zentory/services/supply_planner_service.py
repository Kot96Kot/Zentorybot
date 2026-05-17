from zentory.schemas.supply import (
    SupplyPlannerInput,
    SupplyPlannerReport,
    SupplyPriority,
    SupplyRecommendation,
)
from zentory.services.localization_service import LocalizationService
from zentory.services.replenishment_service import ReplenishmentService


class SupplyPlannerService:
    def __init__(
        self,
        localization_service: LocalizationService | None = None,
        replenishment_service: ReplenishmentService | None = None,
    ) -> None:
        self.localization_service = localization_service or LocalizationService()
        self.replenishment_service = replenishment_service or ReplenishmentService()

    def build_mock_inputs(self, sku: str | None = None) -> list[SupplyPlannerInput]:
        items = [
            SupplyPlannerInput(
                sku="ZNT-COS-001",
                warehouse="Коледино",
                region="Центр",
                stock_qty=18,
                sales_qty_7d=42,
                sales_qty_30d=150,
                sales_qty_prev_30d=120,
                sales_qty_prev_prev_30d=90,
                avg_daily_sales=6.0,
                lead_time_days=5,
                target_coverage_days=30,
                localization_index=0.91,
                logistics_cost=28.0,
                available_for_supply=220,
                is_advertised=True,
            ),
            SupplyPlannerInput(
                sku="ZNT-HOME-002",
                warehouse="Хоругвино",
                region="Поволжье",
                stock_qty=52,
                sales_qty_7d=21,
                sales_qty_30d=80,
                sales_qty_prev_30d=78,
                sales_qty_prev_prev_30d=76,
                avg_daily_sales=3.0,
                lead_time_days=7,
                target_coverage_days=28,
                localization_index=0.48,
                logistics_cost=42.0,
                available_for_supply=120,
            ),
            SupplyPlannerInput(
                sku="ZNT-ACC-003",
                warehouse="Софьино",
                region="Урал",
                stock_qty=240,
                sales_qty_7d=2,
                sales_qty_30d=5,
                sales_qty_prev_30d=6,
                sales_qty_prev_prev_30d=8,
                avg_daily_sales=0.2,
                lead_time_days=10,
                target_coverage_days=30,
                localization_index=0.72,
                logistics_cost=55.0,
                available_for_supply=500,
            ),
        ]
        if sku is None:
            return items
        return [item for item in items if item.sku == sku]

    def plan(self, sku: str | None = None) -> SupplyPlannerReport:
        inputs = self.build_mock_inputs(sku)
        recommendations = [self.recommend(item) for item in inputs]
        warehouses = [self.localization_service.evaluate(item) for item in inputs]
        return SupplyPlannerReport(
            risks=[item for item in recommendations if item.priority in self._risk_priorities()],
            replenishment=[item for item in recommendations if item.recommended_supply_qty > 0],
            warehouses=warehouses,
            recommendations=recommendations,
            ads_alerts=self.ads_alerts(recommendations),
            mock_mode=True,
        )

    def recommend(self, item: SupplyPlannerInput) -> SupplyRecommendation:
        coverage = item.coverage_days
        priority = self.priority_for(item)
        localization = self.localization_service.evaluate(item)
        target_warehouse = (
            localization.target_warehouse
            if localization.redistribution_recommended
            else item.warehouse
        )
        warning_list: list[str] = []
        approval_required = False

        if coverage is None:
            warning_list.append("Нет продаж: coverage нельзя рассчитать без деления на 0")
        elif coverage < 7:
            warning_list.append("Остатка меньше 7 дней")
        elif coverage < 14:
            warning_list.append("Остатка меньше 14 дней")

        if item.is_advertised and (coverage is not None and coverage < 14):
            warning_list.append("Товар в рекламе и остатка мало: нужен alert для AdsAgent")
        if localization.redistribution_recommended:
            warning_list.append(
                "Склад дает плохую локализацию: предложен подсорт/перераспределение"
            )
        if self.is_slow_mover(item):
            warning_list.append("Slow mover: не увеличивать поставку без approval")
            approval_required = True
        if self.has_three_period_growth(item):
            warning_list.append("Продажи растут 3 периода подряд: приоритет отгрузки повышен")

        recommended_qty = self.replenishment_service.supply_quantity(
            stock_qty=item.stock_qty,
            avg_daily_sales=item.avg_daily_sales,
            target_coverage_days=item.target_coverage_days,
            lead_time_days=item.lead_time_days,
            available_for_supply=item.available_for_supply,
            slow_mover=self.is_slow_mover(item),
        )
        if self.is_slow_mover(item):
            recommended_qty = 0

        expected_coverage = self.expected_coverage_days(item, recommended_qty)
        reason = self.reason_for(item, priority, localization.redistribution_recommended)
        return SupplyRecommendation(
            sku=item.sku,
            warehouse=item.warehouse,
            region=item.region,
            recommended_supply_qty=recommended_qty,
            target_warehouse=target_warehouse,
            priority=priority,
            reason=reason,
            expected_coverage_days=expected_coverage,
            localization_impact=localization.localization_impact,
            replenishment_cost=round(recommended_qty * item.logistics_cost, 2),
            warning_list=warning_list,
            approval_required=approval_required,
            mock_mode=True,
        )

    def priority_for(self, item: SupplyPlannerInput) -> SupplyPriority:
        coverage = item.coverage_days
        if coverage is None:
            priority = SupplyPriority.LOW
        elif coverage < 7:
            priority = SupplyPriority.CRITICAL
        elif coverage < 14:
            priority = SupplyPriority.HIGH
        else:
            priority = (
                SupplyPriority.MEDIUM if item.localization_index < 0.65 else SupplyPriority.LOW
            )
        if self.has_three_period_growth(item):
            priority = self._raise_priority(priority)
        if self.is_slow_mover(item):
            return SupplyPriority.MEDIUM
        return priority

    def ads_alerts(self, recommendations: list[SupplyRecommendation]) -> list[dict[str, str]]:
        alerts = []
        for recommendation in recommendations:
            if any("AdsAgent" in warning for warning in recommendation.warning_list):
                alerts.append(
                    {
                        "sku": recommendation.sku,
                        "target_agent": "AdsAgent",
                        "reason": "Товар в рекламе при низком покрытии остатками",
                    }
                )
        return alerts

    @staticmethod
    def expected_coverage_days(item: SupplyPlannerInput, recommended_qty: int) -> float | None:
        if item.avg_daily_sales <= 0:
            return None
        return round((item.stock_qty + recommended_qty) / item.avg_daily_sales, 2)

    @staticmethod
    def is_slow_mover(item: SupplyPlannerInput) -> bool:
        return item.avg_daily_sales < 0.5 or item.sales_qty_30d <= 5

    @staticmethod
    def has_three_period_growth(item: SupplyPlannerInput) -> bool:
        if item.sales_qty_prev_30d is None or item.sales_qty_prev_prev_30d is None:
            return False
        return item.sales_qty_prev_prev_30d < item.sales_qty_prev_30d < item.sales_qty_30d

    @staticmethod
    def reason_for(
        item: SupplyPlannerInput, priority: SupplyPriority, redistribution: bool
    ) -> str:
        parts = [f"coverage={item.coverage_days} дней", f"priority={priority.value}"]
        if redistribution:
            parts.append("плохая локализация склада")
        if item.is_advertised:
            parts.append("SKU в рекламе")
        return "; ".join(parts)

    @staticmethod
    def _raise_priority(priority: SupplyPriority) -> SupplyPriority:
        order = [
            SupplyPriority.LOW,
            SupplyPriority.MEDIUM,
            SupplyPriority.HIGH,
            SupplyPriority.CRITICAL,
        ]
        index = min(order.index(priority) + 1, len(order) - 1)
        return order[index]

    @staticmethod
    def _risk_priorities() -> set[SupplyPriority]:
        return {SupplyPriority.HIGH, SupplyPriority.CRITICAL}

import math

from zentory.schemas.inventory import (
    InventoryPriority,
    InventorySkuInput,
    ReplenishmentRecommendation,
    WarehouseStock,
)


class ReplenishmentService:
    def shipping_recommendation(
        self, item: InventorySkuInput, *, priority: InventoryPriority
    ) -> ReplenishmentRecommendation:
        desired_stock = math.ceil(item.average_daily_sales * item.desired_stock_days)
        incoming = item.transit + item.supply_plan
        suggested_quantity = max(desired_stock - item.total_stock - incoming, 0)
        return ReplenishmentRecommendation(
            recommendation_type="shipment",
            title="Рекомендация по отгрузке",
            description=(
                "Нужно пополнить общий остаток до желаемого запаса "
                f"на {item.desired_stock_days} дней."
            ),
            target_warehouse=item.warehouse,
            target_region=item.region,
            suggested_quantity=suggested_quantity,
            priority=priority,
        )

    def redistribution_recommendation(
        self, item: InventorySkuInput, missing_warehouse: WarehouseStock
    ) -> ReplenishmentRecommendation:
        suggested_quantity = max(math.ceil(item.average_daily_sales * 7), item.minimum_stock)
        return ReplenishmentRecommendation(
            recommendation_type="redistribution",
            title="Рекомендация по подсорту",
            description=(
                "Товар продается, но отсутствует на ключевом складе: "
                f"подсортить {missing_warehouse.warehouse}."
            ),
            target_warehouse=missing_warehouse.warehouse,
            target_region=missing_warehouse.region,
            suggested_quantity=suggested_quantity,
            priority=InventoryPriority.HIGH,
        )

    def slow_mover_recommendation(self, item: InventorySkuInput) -> ReplenishmentRecommendation:
        return ReplenishmentRecommendation(
            recommendation_type="slow_mover",
            title="Slow mover: не усиливать поставку",
            description=(
                "Товар лежит больше 45 дней без движения: нужна распродажа или пересмотр цены."
            ),
            target_warehouse=item.warehouse,
            target_region=item.region,
            suggested_quantity=0,
            priority=InventoryPriority.MEDIUM,
        )

    @staticmethod
    def supply_quantity(
        *,
        stock_qty: int,
        avg_daily_sales: float,
        target_coverage_days: int,
        lead_time_days: int,
        available_for_supply: int,
        slow_mover: bool = False,
    ) -> int:
        if slow_mover or avg_daily_sales <= 0:
            return 0
        target_stock = math.ceil(avg_daily_sales * (target_coverage_days + lead_time_days))
        return min(max(target_stock - stock_qty, 0), max(available_for_supply, 0))

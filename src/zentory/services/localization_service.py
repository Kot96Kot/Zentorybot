from zentory.schemas.supply import SupplyPlannerInput, WarehouseLocalization


class LocalizationService:
    TARGET_WAREHOUSE_BY_REGION = {
        "Центр": "Коледино",
        "Поволжье": "Казань",
        "Северо-Запад": "Санкт-Петербург",
        "Урал": "Екатеринбург",
        "Юг": "Краснодар",
    }

    def evaluate(self, item: SupplyPlannerInput) -> WarehouseLocalization:
        target = self.target_warehouse_for(item.region)
        impact = self.localization_impact(item.localization_index, item.logistics_cost)
        redistribution = item.localization_index < 0.65 or item.warehouse != target
        reason = (
            f"Локализация {item.localization_index:.2f}: лучше держать запас на {target}"
            if redistribution
            else "Локализация склада достаточная"
        )
        return WarehouseLocalization(
            warehouse=item.warehouse,
            region=item.region,
            localization_index=item.localization_index,
            logistics_cost=item.logistics_cost,
            target_warehouse=target,
            localization_impact=impact,
            redistribution_recommended=redistribution,
            reason=reason,
            mock_mode=True,
        )

    def target_warehouse_for(self, region: str) -> str:
        return self.TARGET_WAREHOUSE_BY_REGION.get(region, "Коледино")

    @staticmethod
    def localization_impact(localization_index: float, logistics_cost: float) -> float:
        index_gap = max(0.0, 1.0 - localization_index)
        return round(index_gap * logistics_cost, 2)

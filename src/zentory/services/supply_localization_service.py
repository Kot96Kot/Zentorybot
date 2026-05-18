from zentory.schemas.platform_modules import SupplyLocalizationItem, SupplyLocalizationPlan


class SupplyLocalizationService:
    def build_plan(self) -> SupplyLocalizationPlan:
        return SupplyLocalizationPlan(
            items=[
                SupplyLocalizationItem(
                    sku="WB-MOCK-1",
                    source_warehouse="Коледино",
                    target_warehouse="Софьино",
                    target_region="Центр",
                    transfer_units=120,
                    expected_coverage_days=18.5,
                    reason="ABC A SKU имеет высокий спрос и риск out-of-stock в ключевом регионе.",
                ),
                SupplyLocalizationItem(
                    sku="OZON-MOCK-2",
                    source_warehouse="Хоругвино",
                    target_warehouse="Екатеринбург",
                    target_region="Урал",
                    transfer_units=45,
                    expected_coverage_days=21.0,
                    reason="Локализация снизит срок доставки без изменения цены.",
                ),
            ],
            blocked_actions=[
                "Не создавать реальные поставки без approval.",
                "Не перемещать C-класс, если нет подтвержденного спроса.",
            ],
        )

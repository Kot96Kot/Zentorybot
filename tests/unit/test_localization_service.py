from zentory.schemas.supply import SupplyPlannerInput
from zentory.services.localization_service import LocalizationService


def test_localization_suggests_redistribution_for_bad_index() -> None:
    item = SupplyPlannerInput(
        sku="SKU-LOC",
        warehouse="Хоругвино",
        region="Поволжье",
        stock_qty=40,
        sales_qty_7d=14,
        sales_qty_30d=60,
        avg_daily_sales=2,
        lead_time_days=5,
        target_coverage_days=30,
        localization_index=0.45,
        logistics_cost=50,
        available_for_supply=80,
    )

    result = LocalizationService().evaluate(item)

    assert result.redistribution_recommended is True
    assert result.target_warehouse == "Казань"
    assert result.localization_impact == 27.5


def test_localization_accepts_good_target_warehouse() -> None:
    item = SupplyPlannerInput(
        sku="SKU-OK",
        warehouse="Коледино",
        region="Центр",
        stock_qty=40,
        sales_qty_7d=14,
        sales_qty_30d=60,
        avg_daily_sales=2,
        lead_time_days=5,
        target_coverage_days=30,
        localization_index=0.9,
        logistics_cost=50,
        available_for_supply=80,
    )

    result = LocalizationService().evaluate(item)

    assert result.redistribution_recommended is False
    assert result.target_warehouse == "Коледино"

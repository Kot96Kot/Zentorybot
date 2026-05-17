from zentory.schemas.supply import SupplyPlannerInput, SupplyPriority
from zentory.services.supply_planner_service import SupplyPlannerService


def test_supply_planner_marks_critical_under_seven_days_and_ads_alert() -> None:
    service = SupplyPlannerService()
    item = SupplyPlannerInput(
        sku="SKU-ADS",
        warehouse="Коледино",
        region="Центр",
        stock_qty=12,
        sales_qty_7d=28,
        sales_qty_30d=120,
        avg_daily_sales=4,
        lead_time_days=5,
        target_coverage_days=30,
        localization_index=0.9,
        logistics_cost=30,
        available_for_supply=200,
        is_advertised=True,
    )

    recommendation = service.recommend(item)

    assert recommendation.priority == SupplyPriority.CRITICAL
    assert recommendation.recommended_supply_qty == 128
    assert recommendation.expected_coverage_days == 35
    assert any("AdsAgent" in warning for warning in recommendation.warning_list)


def test_supply_planner_high_priority_under_fourteen_days() -> None:
    recommendation = SupplyPlannerService().recommend(
        SupplyPlannerInput(
            sku="SKU-HIGH",
            warehouse="Казань",
            region="Поволжье",
            stock_qty=36,
            sales_qty_7d=21,
            sales_qty_30d=90,
            avg_daily_sales=3,
            lead_time_days=4,
            target_coverage_days=24,
            localization_index=0.8,
            logistics_cost=25,
            available_for_supply=50,
        )
    )

    assert recommendation.priority == SupplyPriority.HIGH
    assert "меньше 14" in " ".join(recommendation.warning_list)


def test_slow_mover_does_not_increase_supply_without_approval() -> None:
    recommendation = SupplyPlannerService().recommend(
        SupplyPlannerInput(
            sku="SKU-SLOW",
            warehouse="Софьино",
            region="Урал",
            stock_qty=100,
            sales_qty_7d=1,
            sales_qty_30d=4,
            avg_daily_sales=0.1,
            lead_time_days=10,
            target_coverage_days=30,
            localization_index=0.75,
            logistics_cost=40,
            available_for_supply=500,
        )
    )

    assert recommendation.recommended_supply_qty == 0
    assert recommendation.approval_required is True
    assert any("Slow mover" in warning for warning in recommendation.warning_list)


def test_three_period_growth_raises_priority() -> None:
    recommendation = SupplyPlannerService().recommend(
        SupplyPlannerInput(
            sku="SKU-GROWTH",
            warehouse="Коледино",
            region="Центр",
            stock_qty=60,
            sales_qty_7d=25,
            sales_qty_30d=100,
            sales_qty_prev_30d=70,
            sales_qty_prev_prev_30d=40,
            avg_daily_sales=3,
            lead_time_days=5,
            target_coverage_days=30,
            localization_index=0.95,
            logistics_cost=20,
            available_for_supply=100,
        )
    )

    assert recommendation.priority == SupplyPriority.MEDIUM
    assert any("растут 3 периода" in warning for warning in recommendation.warning_list)


def test_supply_report_contains_risks_replenishment_and_ads_alerts() -> None:
    report = SupplyPlannerService().plan()

    assert report.mock_mode is True
    assert report.risks
    assert report.replenishment
    assert report.warehouses
    assert report.ads_alerts[0]["target_agent"] == "AdsAgent"

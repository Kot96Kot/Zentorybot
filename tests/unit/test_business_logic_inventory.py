from zentory.schemas.inventory import InventoryPriority, InventorySkuInput, InventoryStatus
from zentory.services.inventory_service import InventoryService


def _item(**overrides: object) -> InventorySkuInput:
    data = {
        "sku": "SKU-STOCK-1",
        "total_stock": 100,
        "sales_7d": 70,
        "sales_14d": 140,
        "sales_30d": 300,
        "average_daily_sales": 10.0,
        "coverage_days": 10.0,
        "warehouse": "Коледино",
        "region": "Центр",
        "transit": 0,
        "supply_plan": 0,
        "minimum_stock": 30,
        "desired_stock_days": 21,
    }
    data.update(overrides)
    return InventorySkuInput(**data)


def test_stock_less_than_7_days_is_critical() -> None:
    report = InventoryService().analyze_item(_item(total_stock=50, coverage_days=5.0))

    assert report.status == InventoryStatus.CRITICAL
    assert report.priority == InventoryPriority.CRITICAL
    assert report.out_of_stock_risk is True


def test_stock_less_than_14_days_is_warning() -> None:
    report = InventoryService().analyze_item(_item(total_stock=120, coverage_days=12.0))

    assert report.status == InventoryStatus.WARNING
    assert report.priority == InventoryPriority.HIGH
    assert report.telegram_alert is not None


def test_out_of_stock_raises_task_priority() -> None:
    report = InventoryService().analyze_item(
        _item(total_stock=0, average_daily_sales=10.0, coverage_days=0.0)
    )

    assert report.status == InventoryStatus.CRITICAL
    assert report.priority == InventoryPriority.CRITICAL
    assert report.recommendations
    assert all(
        recommendation.priority == InventoryPriority.CRITICAL
        for recommendation in report.recommendations
    )


def test_advertised_sku_with_low_stock_alerts_ads_agent() -> None:
    report = InventoryService().analyze_item(
        _item(total_stock=45, coverage_days=4.5, is_advertised=True)
    )

    assert report.alerts_for_ads_agent
    assert "AdsAgent" in report.alerts_for_ads_agent[0]

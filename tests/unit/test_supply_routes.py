import asyncio

from zentory.api.routers.supply import (
    supply_replenishment,
    supply_risks,
    supply_sku,
    supply_warehouses,
)
from zentory.services.supply_planner_service import SupplyPlannerService


def test_supply_routes_return_mock_contracts() -> None:
    service = SupplyPlannerService()

    risks = asyncio.run(supply_risks(service))
    replenishment = asyncio.run(supply_replenishment(service))
    warehouses = asyncio.run(supply_warehouses(service))
    sku = asyncio.run(supply_sku("ZNT-COS-001", service))

    assert risks["mock_mode"] is True
    assert risks["risks"]
    assert risks["ads_alerts"]
    assert replenishment["replenishment"][0]["recommended_supply_qty"] > 0
    assert warehouses["warehouses"]
    assert sku["recommendations"][0]["sku"] == "ZNT-COS-001"

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_supply_planner_service
from zentory.services.supply_planner_service import SupplyPlannerService

router = APIRouter(prefix="/supply", tags=["supply"])
SupplyPlannerDependency = Annotated[SupplyPlannerService, Depends(get_supply_planner_service)]


@router.get("/risks")
async def supply_risks(service: SupplyPlannerDependency) -> dict[str, Any]:
    return service.plan().model_dump(mode="json", include={"risks", "ads_alerts", "mock_mode"})


@router.get("/replenishment")
async def supply_replenishment(service: SupplyPlannerDependency) -> dict[str, Any]:
    return service.plan().model_dump(
        mode="json", include={"replenishment", "ads_alerts", "mock_mode"}
    )


@router.get("/warehouses")
async def supply_warehouses(service: SupplyPlannerDependency) -> dict[str, Any]:
    return service.plan().model_dump(mode="json", include={"warehouses", "mock_mode"})


@router.get("/sku/{sku}")
async def supply_sku(sku: str, service: SupplyPlannerDependency) -> dict[str, Any]:
    return service.plan(sku=sku).model_dump(mode="json")

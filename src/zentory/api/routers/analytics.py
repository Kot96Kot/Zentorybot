from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_forecast_service
from zentory.schemas.abc import ABCMetric
from zentory.services.forecast_service import ForecastService

router = APIRouter(prefix="/analytics", tags=["analytics"])
ForecastServiceDependency = Annotated[ForecastService, Depends(get_forecast_service)]


@router.get("/abc")
async def abc_default(service: ForecastServiceDependency) -> dict[str, Any]:
    return service.abc_report(metric=ABCMetric.REVENUE).model_dump(mode="json")


@router.get("/abc/{metric}")
async def abc_by_metric(metric: ABCMetric, service: ForecastServiceDependency) -> dict[str, Any]:
    return service.abc_report(metric=metric).model_dump(mode="json")


@router.get("/forecast")
async def forecast(service: ForecastServiceDependency) -> dict[str, Any]:
    return service.full_report().model_dump(mode="json")


@router.get("/forecast/{sku}")
async def forecast_sku(sku: str, service: ForecastServiceDependency) -> dict[str, Any]:
    item = service.sku_forecast(sku)
    return {
        "mock_mode": True,
        "sku": sku,
        "forecast": item.model_dump(mode="json") if item else None,
    }


@router.get("/stock-forecast")
async def stock_forecast(service: ForecastServiceDependency) -> dict[str, Any]:
    return service.stock_forecast_report().model_dump(mode="json")

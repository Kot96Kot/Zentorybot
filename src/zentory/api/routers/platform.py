from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_platform_modules_service
from zentory.services.platform_modules_service import PlatformModulesService

router = APIRouter(prefix="/platform", tags=["platform-modules"])

PlatformModulesDependency = Annotated[
    PlatformModulesService, Depends(get_platform_modules_service)
]


@router.get("/modules")
def platform_modules(service: PlatformModulesDependency) -> dict[str, Any]:
    snapshot = service.build_snapshot()
    return {
        "mock": True,
        "summary": snapshot.to_manager_summary(),
        "modules": snapshot.model_dump(mode="json"),
    }


@router.get("/forecast-abc")
def forecast_abc(service: PlatformModulesDependency) -> dict[str, Any]:
    return service.forecast_abc.build_report().model_dump(mode="json")


@router.get("/supply-localization")
def supply_localization(service: PlatformModulesDependency) -> dict[str, Any]:
    return service.supply.build_plan().model_dump(mode="json")


@router.get("/content-ctr")
def content_ctr(service: PlatformModulesDependency) -> dict[str, Any]:
    return service.content_ctr.build_report().model_dump(mode="json")


@router.get("/finance-checker")
def finance_checker(service: PlatformModulesDependency) -> dict[str, Any]:
    return service.finance.build_report().model_dump(mode="json")


@router.get("/learning-loop")
def learning_loop(service: PlatformModulesDependency) -> dict[str, Any]:
    return service.learning_loop.build_report().model_dump(mode="json")


@router.get("/data-contracts")
def data_contracts(service: PlatformModulesDependency) -> dict[str, Any]:
    return service.data_contracts.build_report().model_dump(mode="json")

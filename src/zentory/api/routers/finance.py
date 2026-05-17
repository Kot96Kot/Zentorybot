from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_finance_checker_service
from zentory.services.finance_checker_service import FinanceCheckerService

router = APIRouter(prefix="/finance", tags=["finance"])
FinanceCheckerDependency = Annotated[FinanceCheckerService, Depends(get_finance_checker_service)]


@router.get("/check")
async def finance_check(service: FinanceCheckerDependency) -> dict[str, Any]:
    return service.check().model_dump(mode="json")


@router.get("/pnl")
async def finance_pnl(service: FinanceCheckerDependency) -> dict[str, Any]:
    return service.pnl().model_dump(mode="json")


@router.get("/unit/{sku}")
async def finance_unit(sku: str, service: FinanceCheckerDependency) -> dict[str, Any]:
    unit = service.unit(sku)
    return {"mock_mode": True, "sku": sku, "unit": unit.model_dump(mode="json") if unit else None}

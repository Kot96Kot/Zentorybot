from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_reports_service
from zentory.services.reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])

ReportsServiceDependency = Annotated[ReportsService, Depends(get_reports_service)]


@router.get("/daily")
async def daily_report(service: ReportsServiceDependency) -> dict[str, Any]:
    return await service.daily_report()

from typing import Annotated

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_sku_intelligence_service
from zentory.schemas.sku_intelligence import SKUIntelligenceCard
from zentory.services.sku_intelligence_service import SKUIntelligenceService

router = APIRouter(prefix="/sku", tags=["sku"])

SKUIntelligenceDependency = Annotated[
    SKUIntelligenceService, Depends(get_sku_intelligence_service)
]


@router.get("/{sku}/intelligence", response_model=SKUIntelligenceCard)
async def get_sku_intelligence(
    sku: str, service: SKUIntelligenceDependency
) -> SKUIntelligenceCard:
    return service.build_card(sku)

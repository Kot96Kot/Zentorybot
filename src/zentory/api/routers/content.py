from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_content_ctr_service
from zentory.schemas.content_ctr import ContentBriefCTR
from zentory.services.content_ctr_service import ContentCTRService

router = APIRouter(prefix="/content", tags=["content"])
ContentCTRDependency = Annotated[ContentCTRService, Depends(get_content_ctr_service)]


@router.post("/brief")
async def content_brief(payload: dict[str, Any], service: ContentCTRDependency) -> dict[str, Any]:
    return service.build_brief(payload).model_dump(mode="json")


@router.post("/hypotheses")
async def content_hypotheses(
    payload: dict[str, Any], service: ContentCTRDependency
) -> dict[str, Any]:
    brief = service.build_brief(payload)
    return {
        "brief": brief.model_dump(mode="json"),
        "hypotheses": [item.model_dump(mode="json") for item in service.generate_hypotheses(brief)],
        "mock_mode": True,
    }


@router.post("/prompts")
async def content_prompts(
    payload: dict[str, Any], service: ContentCTRDependency
) -> dict[str, Any]:
    brief = (
        ContentBriefCTR(**payload)
        if payload.get("sku") and payload.get("target_audience")
        else service.build_brief(payload)
    )
    hypotheses = service.generate_hypotheses(brief)[:3]
    return {
        "brief": brief.model_dump(mode="json"),
        "prompts": [
            item.model_dump(mode="json")
            for item in service.generate_prompts(brief, hypotheses)
        ],
        "mock_mode": True,
    }


@router.get("/sku/{sku}")
async def content_sku(sku: str, service: ContentCTRDependency) -> dict[str, Any]:
    return service.build_for_sku(sku).model_dump(mode="json")

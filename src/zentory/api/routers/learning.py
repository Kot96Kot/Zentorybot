from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.api.dependencies import get_action_result_service
from zentory.schemas.learning import ActionResultRequest
from zentory.services.action_result_service import ActionResultService

router = APIRouter(prefix="/learning", tags=["learning"])
ActionResultDependency = Annotated[ActionResultService, Depends(get_action_result_service)]


def _dump(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")


@router.post("/action-result")
async def action_result(
    request: ActionResultRequest, service: ActionResultDependency
) -> dict[str, Any]:
    record = service.record_action_result(request)
    return {"mock_mode": True, "action": _dump(record)}


@router.get("/actions")
async def learning_actions(service: ActionResultDependency) -> dict[str, Any]:
    actions = service.list_actions()
    return {
        "mock_mode": True,
        "summary": _dump(service.summary()),
        "actions": [_dump(action) for action in actions],
    }


@router.get("/sku/{sku}")
async def learning_sku(sku: str, service: ActionResultDependency) -> dict[str, Any]:
    actions = service.list_by_sku(sku)
    return {
        "mock_mode": True,
        "sku": sku,
        "summary": _dump(service.summary(sku)),
        "actions": [_dump(action) for action in actions],
    }

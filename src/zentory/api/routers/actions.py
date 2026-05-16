from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from zentory.actions.registry import ActionRegistry
from zentory.actions.schemas import ActionApprovalRequest, ActionPreviewRequest
from zentory.agents.orchestrator import Orchestrator
from zentory.api.dependencies import get_action_registry, get_orchestrator
from zentory.core.errors import ActionNotFoundError

router = APIRouter(prefix="/actions", tags=["actions"])

OrchestratorDependency = Annotated[Orchestrator, Depends(get_orchestrator)]
ActionRegistryDependency = Annotated[ActionRegistry, Depends(get_action_registry)]


@router.post("/preview")
async def preview_action(
    request: ActionPreviewRequest, orchestrator: OrchestratorDependency
) -> dict[str, Any]:
    decision = await orchestrator.handle_event(request.model_dump())
    return decision.model_dump(mode="json")


@router.post("/approve")
async def approve_action(
    request: ActionApprovalRequest, registry: ActionRegistryDependency
) -> dict[str, Any]:
    try:
        action = registry.approve(request.action_id)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"approved_by": request.approved_by, "action": action.model_dump(mode="json")}

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from zentory.actions.action_center import ActionCenter
from zentory.actions.registry import ActionRegistry
from zentory.actions.schemas import ActionApprovalRequest, ActionPreviewRequest
from zentory.agents.orchestrator import Orchestrator
from zentory.api.dependencies import get_action_center, get_action_registry, get_orchestrator
from zentory.core.errors import ActionNotFoundError
from zentory.schemas.actions import ActionCreateRequest

router = APIRouter(prefix="/actions", tags=["actions"])

OrchestratorDependency = Annotated[Orchestrator, Depends(get_orchestrator)]
ActionRegistryDependency = Annotated[ActionRegistry, Depends(get_action_registry)]
ActionCenterDependency = Annotated[ActionCenter, Depends(get_action_center)]


def _dump(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")


@router.post("/preview")
async def preview_action(
    request: ActionPreviewRequest, orchestrator: OrchestratorDependency
) -> dict[str, Any]:
    """Preview orchestrator proposals for an event without executing anything."""

    decision = await orchestrator.handle_event(request.model_dump())
    return decision.model_dump(mode="json")


@router.post("/approve")
async def approve_action(
    request: ActionApprovalRequest, registry: ActionRegistryDependency
) -> dict[str, Any]:
    """Approve an orchestrator action stored in the action registry.

    This route is retained for Telegram and orchestrator compatibility while the richer
    Action Center routes below expose the full lifecycle for persisted action cards.
    """

    try:
        action = registry.approve(request.action_id)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"approved_by": request.approved_by, "action": action.model_dump(mode="json")}


@router.post("")
async def create_action(
    request: ActionCreateRequest, action_center: ActionCenterDependency
) -> dict[str, Any]:
    """Create an Action Center card with evidence, risk and rollback metadata."""

    action = action_center.create_action(**request.model_dump())
    return {"mock": True, "action": _dump(action)}


@router.get("")
async def list_recent_actions(
    action_center: ActionCenterDependency, limit: int = 20
) -> dict[str, Any]:
    """Return recent Action Center cards in newest-first order."""

    actions = action_center.list_recent_actions(limit=limit)
    return {"mock": True, "actions": [_dump(action) for action in actions]}


@router.get("/pending")
async def list_pending_actions(action_center: ActionCenterDependency) -> dict[str, Any]:
    """Return actions that still need a decision or are ready to execute."""

    actions = action_center.list_pending_actions()
    return {"mock": True, "actions": [_dump(action) for action in actions]}


@router.get("/{action_id}")
async def get_action(action_id: str, action_center: ActionCenterDependency) -> dict[str, Any]:
    try:
        action = action_center.get_action(action_id)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"mock": True, "action": _dump(action)}


@router.get("/{action_id}/preview")
async def preview_action_card(
    action_id: str, action_center: ActionCenterDependency
) -> dict[str, Any]:
    """Render an Action Center approval card for Telegram/web UI consumption."""

    try:
        preview = action_center.preview_action(action_id)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"mock": True, "preview": _dump(preview)}


@router.post("/{action_id}/approve")
async def approve_action_card(
    action_id: str, action_center: ActionCenterDependency, approved_by: str = "mock_user"
) -> dict[str, Any]:
    try:
        action = action_center.approve_action(action_id, approved_by=approved_by)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"mock": True, "approved_by": approved_by, "action": _dump(action)}


@router.post("/{action_id}/reject")
async def reject_action_card(
    action_id: str, action_center: ActionCenterDependency, rejected_by: str = "mock_user"
) -> dict[str, Any]:
    try:
        action = action_center.reject_action(action_id, rejected_by=rejected_by)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"mock": True, "rejected_by": rejected_by, "action": _dump(action)}


@router.post("/{action_id}/execute")
async def execute_action_card(
    action_id: str, action_center: ActionCenterDependency
) -> dict[str, Any]:
    try:
        action = action_center.execute_action(action_id)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"mock": True, "action": _dump(action)}


@router.post("/{action_id}/rollback")
async def rollback_action_card(
    action_id: str, action_center: ActionCenterDependency
) -> dict[str, Any]:
    try:
        action = action_center.rollback_action(action_id)
    except ActionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"mock": True, "action": _dump(action)}

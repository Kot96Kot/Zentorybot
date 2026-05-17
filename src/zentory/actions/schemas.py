from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel


class Action(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    agent_name: str = "unknown_agent"
    action_type: str
    title: str
    description: str
    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    approval_mode: ApprovalMode = ApprovalMode.NONE
    status: ActionStatus = ActionStatus.PROPOSED
    rollback_available: bool = False
    explanation: str = ""
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    idempotency_key: str | None = None


class ActionPreviewRequest(BaseModel):
    event_type: str = "manual_preview"
    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)


class ActionApprovalRequest(BaseModel):
    action_id: str
    approved_by: str = "mock_user"

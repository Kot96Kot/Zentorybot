from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel


class ActionEvidence(BaseModel):
    source: str
    label: str
    value: Any


class ActionRecord(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    agent_name: str
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
    evidence: list[ActionEvidence] = Field(default_factory=list)


class ActionPreview(BaseModel):
    action_id: str
    title: str
    proposed_by: str
    reason: str
    risk_level: RiskLevel
    approval_mode: ApprovalMode
    data_used: list[ActionEvidence]
    changes: dict[str, dict[str, Any]]
    rollback_available: bool
    buttons: list[dict[str, str]]
    mock: bool = True


class ActionCreateRequest(BaseModel):
    agent_name: str = "MockAgent"
    action_type: str
    title: str
    description: str
    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    approval_mode: ApprovalMode = ApprovalMode.NONE
    rollback_available: bool = False
    explanation: str = ""
    evidence: list[ActionEvidence] = Field(default_factory=list)

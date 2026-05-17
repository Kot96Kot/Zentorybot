from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class LearningEvaluation(StrEnum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


class LearningActionStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"


class LearningActionProposed(BaseModel):
    action_id: str
    agent: str
    sku: str
    recommendation: str
    expected_effect: str
    metric_before: float
    metric_name: str = "target_metric"
    proposed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)
    mock_mode: bool = True


class LearningActionApproval(BaseModel):
    approved_by: str = "mock_user"
    approved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    mock_mode: bool = True


class LearningActionExecution(BaseModel):
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    execution_status: LearningActionStatus = LearningActionStatus.EXECUTED
    mock_mode: bool = True


class ActionResultRequest(BaseModel):
    action_id: str
    agent: str = "MockAgent"
    sku: str
    recommendation: str
    expected_effect: str
    metric_before: float
    metric_after: float | None = None
    metric_name: str = "target_metric"
    approved_by: str = "mock_user"
    approved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    execution_status: LearningActionStatus = LearningActionStatus.EXECUTED
    metadata: dict[str, Any] = Field(default_factory=dict)
    mock_mode: bool = True


class LearningActionRecord(BaseModel):
    action_id: str
    agent: str
    sku: str
    recommendation: str
    expected_effect: str
    metric_name: str
    metric_before: float
    metric_after: float | None = None
    effect: float | None = None
    success_score: float | None = None
    conclusion: str
    status: LearningEvaluation = LearningEvaluation.INCONCLUSIVE
    action_success: bool = False
    proposed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    approved_by: str | None = None
    approved_at: datetime | None = None
    executed_at: datetime | None = None
    execution_status: LearningActionStatus | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    mock_mode: bool = True


class LearningSummary(BaseModel):
    total_actions: int
    successful_actions: int
    partial_success_actions: int
    failed_actions: int
    inconclusive_actions: int
    strengthen_rules: list[str] = Field(default_factory=list)
    mock_mode: bool = True

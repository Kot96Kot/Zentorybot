from zentory.schemas.learning import (
    ActionResultRequest,
    LearningActionApproval,
    LearningActionExecution,
    LearningActionProposed,
    LearningActionRecord,
    LearningSummary,
)
from zentory.services.learning_loop_service import LearningLoopService


class ActionResultService:
    def __init__(self, learning_loop: LearningLoopService | None = None) -> None:
        self.learning_loop = learning_loop or LearningLoopService()

    def record_action_result(self, request: ActionResultRequest) -> LearningActionRecord:
        proposed = LearningActionProposed(
            action_id=request.action_id,
            agent=request.agent,
            sku=request.sku,
            recommendation=request.recommendation,
            expected_effect=request.expected_effect,
            metric_before=request.metric_before,
            metric_name=request.metric_name,
            metadata=request.metadata,
            mock_mode=True,
        )
        self.learning_loop.record_proposed(proposed)
        self.learning_loop.record_approved(
            request.action_id,
            LearningActionApproval(
                approved_by=request.approved_by,
                approved_at=request.approved_at,
                mock_mode=True,
            ),
        )
        self.learning_loop.record_executed(
            request.action_id,
            LearningActionExecution(
                executed_at=request.executed_at,
                execution_status=request.execution_status,
                mock_mode=True,
            ),
        )
        return self.learning_loop.record_metric_after(request.action_id, request.metric_after)

    def get_action(self, action_id: str) -> LearningActionRecord | None:
        for action in self.list_actions():
            if action.action_id == action_id:
                return action
        return None

    def list_actions(self) -> list[LearningActionRecord]:
        return self.learning_loop.list_actions()

    def list_by_sku(self, sku: str) -> list[LearningActionRecord]:
        return self.learning_loop.get_by_sku(sku)

    def summary(self, sku: str | None = None) -> LearningSummary:
        records = self.list_by_sku(sku) if sku is not None else None
        return self.learning_loop.summary(records)

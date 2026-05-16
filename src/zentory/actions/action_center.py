from typing import Any

from zentory.actions.action_executor import ActionExecutor
from zentory.actions.action_preview import ActionPreviewBuilder
from zentory.actions.action_repository import ActionRepository
from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel
from zentory.schemas.actions import ActionEvidence, ActionPreview, ActionRecord
from zentory.services.audit_service import AuditService


class ActionCenter:
    def __init__(
        self,
        repository: ActionRepository | None = None,
        executor: ActionExecutor | None = None,
        preview_builder: ActionPreviewBuilder | None = None,
        audit_service: AuditService | None = None,
    ) -> None:
        self.audit_service = audit_service or AuditService()
        self.repository = repository or ActionRepository()
        self.executor = executor or ActionExecutor(audit_service=self.audit_service)
        self.preview_builder = preview_builder or ActionPreviewBuilder()

    def create_action(
        self,
        *,
        agent_name: str,
        action_type: str,
        title: str,
        description: str,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
        risk_level: RiskLevel = RiskLevel.LOW,
        approval_mode: ApprovalMode = ApprovalMode.NONE,
        rollback_available: bool = False,
        explanation: str = "",
        evidence: list[ActionEvidence] | list[dict[str, Any]] | None = None,
    ) -> ActionRecord:
        action = ActionRecord(
            agent_name=agent_name,
            action_type=action_type,
            title=title,
            description=description,
            before_state=before_state or {},
            after_state=after_state or {},
            payload=payload or {},
            risk_level=risk_level,
            approval_mode=approval_mode,
            rollback_available=rollback_available,
            explanation=explanation,
            evidence=[self._evidence(item) for item in evidence or []],
        )
        self.repository.save(action)
        self.audit_service.record_sync(
            {
                "event_type": "action_center_action_created",
                "action_id": action.action_id,
                "agent_name": action.agent_name,
                "action_type": action.action_type,
                "risk_level": action.risk_level,
                "approval_mode": action.approval_mode,
                "status": action.status,
                "mock": True,
            }
        )
        return action

    def preview_action(self, action_id: str) -> ActionPreview:
        return self.preview_builder.build(self.repository.get(action_id))

    def approve_action(self, action_id: str, *, approved_by: str = "mock_user") -> ActionRecord:
        action = self.repository.update_status(action_id, ActionStatus.APPROVED)
        self.audit_service.record_sync(
            {
                "event_type": "action_center_action_approved",
                "action_id": action.action_id,
                "approved_by": approved_by,
                "mock": True,
            }
        )
        return action

    def reject_action(self, action_id: str, *, rejected_by: str = "mock_user") -> ActionRecord:
        action = self.repository.update_status(action_id, ActionStatus.REJECTED)
        self.audit_service.record_sync(
            {
                "event_type": "action_center_action_rejected",
                "action_id": action.action_id,
                "rejected_by": rejected_by,
                "mock": True,
            }
        )
        return action

    def execute_action(self, action_id: str) -> ActionRecord:
        action = self.repository.get(action_id)
        if action.status == ActionStatus.REJECTED:
            self.audit_service.record_sync(
                {
                    "event_type": "action_center_execution_blocked_rejected",
                    "action_id": action.action_id,
                    "mock": True,
                }
            )
            return action
        if action.approval_mode != ApprovalMode.NONE and action.status != ActionStatus.APPROVED:
            self.audit_service.record_sync(
                {
                    "event_type": "action_center_execution_blocked_without_approval",
                    "action_id": action.action_id,
                    "approval_mode": action.approval_mode,
                    "mock": True,
                }
            )
            return action
        executed = self.executor.execute(action)
        return self.repository.save(executed)

    def rollback_action(self, action_id: str) -> ActionRecord:
        action = self.repository.get(action_id)
        rolled_back = self.executor.rollback(action)
        return self.repository.save(rolled_back)

    def list_pending_actions(self) -> list[ActionRecord]:
        return self.repository.list_pending()

    def list_recent_actions(self, *, limit: int = 20) -> list[ActionRecord]:
        return self.repository.list_recent(limit=limit)

    @staticmethod
    def _evidence(evidence: ActionEvidence | dict[str, Any]) -> ActionEvidence:
        if isinstance(evidence, ActionEvidence):
            return evidence
        return ActionEvidence(**evidence)

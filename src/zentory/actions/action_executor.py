from zentory.core.enums import ActionStatus
from zentory.schemas.actions import ActionRecord
from zentory.services.audit_service import AuditService


class ActionExecutor:
    def __init__(self, audit_service: AuditService | None = None) -> None:
        self.audit_service = audit_service or AuditService()

    def execute(self, action: ActionRecord) -> ActionRecord:
        action.status = ActionStatus.EXECUTED
        action.payload["mock_execution"] = True
        action.payload["mock_execution_count"] = action.payload.get("mock_execution_count", 0) + 1
        action.payload["external_api_called"] = False
        self.audit_service.record_sync(
            {
                "event_type": "action_center_action_executed",
                "action_id": action.action_id,
                "action_type": action.action_type,
                "agent_name": action.agent_name,
                "mock": True,
                "external_api_called": False,
            }
        )
        return action

    def rollback(self, action: ActionRecord) -> ActionRecord:
        if not action.rollback_available:
            self.audit_service.record_sync(
                {
                    "event_type": "action_center_rollback_unavailable",
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "mock": True,
                }
            )
            return action
        action.status = ActionStatus.ROLLED_BACK
        action.payload["mock_rollback"] = True
        action.payload["external_api_called"] = False
        self.audit_service.record_sync(
            {
                "event_type": "action_center_action_rolled_back",
                "action_id": action.action_id,
                "action_type": action.action_type,
                "agent_name": action.agent_name,
                "mock": True,
                "external_api_called": False,
            }
        )
        return action

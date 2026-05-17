from zentory.actions.schemas import Action
from zentory.core.enums import ActionStatus
from zentory.core.errors import ActionNotFoundError, DuplicateActionError, SafeModeViolationError
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.safety_engine import SafetyEngine
from zentory.services.audit_service import AuditService
from zentory.services.idempotency import IdempotencyStore, idempotency_key
from zentory.services.safe_mode import SafeModeService


class ActionRegistry:
    def __init__(
        self,
        audit_service: AuditService | None = None,
        idempotency_store: IdempotencyStore | None = None,
        safe_mode: SafeModeService | None = None,
        safety_engine: SafetyEngine | None = None,
    ) -> None:
        self._actions: dict[str, Action] = {}
        self.audit_service = audit_service or AuditService()
        self.idempotency_store = idempotency_store or IdempotencyStore()
        self.safe_mode = safe_mode or SafeModeService(enabled=True)
        self.safety_engine = safety_engine or SafetyEngine(
            mode=AutomationMode.AUTO, audit_service=self.audit_service
        )

    def register(self, action: Action) -> Action:
        if action.idempotency_key is None:
            action.idempotency_key = idempotency_key(
                {
                    "action_type": action.action_type,
                    "title": action.title,
                    "payload": action.payload,
                }
            )
        self._actions[action.action_id] = action
        self.audit_service.record_sync(
            {
                "event_type": "action_registered",
                "action_id": action.action_id,
                "action_type": action.action_type,
                "status": action.status,
                "risk_level": action.risk_level,
                "approval_mode": action.approval_mode,
                "idempotency_key": action.idempotency_key,
                "mock": True,
            }
        )
        return action

    def find(self, action_id: str) -> Action:
        try:
            return self._actions[action_id]
        except KeyError as exc:
            raise ActionNotFoundError(f"Action {action_id} not found") from exc

    def approve(self, action_id: str) -> Action:
        action = self.find(action_id)
        action.status = ActionStatus.APPROVED
        self.audit_service.record_sync(
            {
                "event_type": "action_approved",
                "action_id": action.action_id,
                "action_type": action.action_type,
                "status": action.status,
                "mock": True,
            }
        )
        return action

    def reject(self, action_id: str) -> Action:
        action = self.find(action_id)
        action.status = ActionStatus.REJECTED
        self.audit_service.record_sync(
            {
                "event_type": "action_rejected",
                "action_id": action.action_id,
                "action_type": action.action_type,
                "status": action.status,
                "mock": True,
            }
        )
        return action

    def execute_mock(self, action_id: str, *, force: bool = False) -> Action:
        action = self.find(action_id)
        try:
            safety_decision = self.safety_engine.evaluate(action)
            if not safety_decision.allowed_to_execute and not force:
                action.payload["safety_blocked"] = True
                self.audit_service.record_sync(
                    {
                        "event_type": "safety_blocked_execution",
                        "action_id": action.action_id,
                        "action_type": action.action_type,
                        "status": action.status,
                        "risk_level": action.risk_level,
                        "approval_mode": action.approval_mode,
                        "automation_mode": safety_decision.automation_mode,
                        "reasons": safety_decision.reasons,
                        "mock": True,
                    }
                )
                return action
            self.safe_mode.ensure_can_execute(action, force=force)
            key = action.idempotency_key or idempotency_key(action.model_dump(mode="json"))
            self.idempotency_store.execute_once(key, lambda: action.action_id)
            action.status = ActionStatus.EXECUTED
            action.payload["mock_execution"] = True
            action.payload["mock_execution_count"] = (
                action.payload.get("mock_execution_count", 0) + 1
            )
            self.audit_service.record_sync(
                {
                    "event_type": "action_executed",
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "status": action.status,
                    "idempotency_key": key,
                    "mock": True,
                }
            )
            return action
        except DuplicateActionError:
            action.payload["idempotency_duplicate"] = True
            self.audit_service.record_sync(
                {
                    "event_type": "duplicate_action_blocked",
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "status": action.status,
                    "idempotency_key": action.idempotency_key,
                    "mock": True,
                }
            )
            return action
        except SafeModeViolationError:
            action.payload["safe_mode_blocked"] = True
            self.audit_service.record_sync(
                {
                    "event_type": "safe_mode_blocked_execution",
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "status": action.status,
                    "mock": True,
                }
            )
            return action

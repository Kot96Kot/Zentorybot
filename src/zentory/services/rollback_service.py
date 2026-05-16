from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from zentory.services.audit_service import AuditService


@dataclass(slots=True)
class RollbackPlan:
    action_id: str
    action_type: str
    payload: dict[str, Any]
    rollback_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    executed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "rollback_id": self.rollback_id,
            "action_id": self.action_id,
            "action_type": self.action_type,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "executed": self.executed,
            "mock": True,
        }


class RollbackService:
    def __init__(self, audit_service: AuditService | None = None) -> None:
        self.audit_service = audit_service or AuditService()
        self._plans: dict[str, RollbackPlan] = {}

    def create_plan(
        self, action_id: str, action_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        plan = RollbackPlan(action_id=action_id, action_type=action_type, payload=payload)
        self._plans[action_id] = plan
        result = plan.to_dict()
        self.audit_service.record_sync({"event_type": "rollback_plan_created", **result})
        return result

    def rollback(self, action_id: str) -> dict[str, Any]:
        plan = self._plans.get(action_id)
        if plan is None:
            result = {
                "status": "rollback unavailable",
                "problem": f"для action_id={action_id} нет rollback-плана",
                "reason": "действие не выполнялось или план отката не был создан",
                "recommendation": "проверьте /alerts или передайте корректный action_id",
                "risk": "MEDIUM",
                "action_id": action_id,
                "mock": True,
            }
        else:
            plan.executed = True
            result = {
                "status": "rollback completed",
                "problem": f"действие {action_id} откатано в mock-режиме",
                "reason": "найден сохраненный rollback-план",
                "recommendation": "проверьте /status и /daily после отката",
                "risk": "LOW",
                "action_id": action_id,
                "rollback_id": plan.rollback_id,
                "mock": True,
            }
        self.audit_service.record_sync({"event_type": "rollback_requested", **result})
        return result

    def list_plans(self) -> list[dict[str, Any]]:
        return [plan.to_dict() for plan in self._plans.values()]

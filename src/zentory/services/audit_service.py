from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from zentory.core.logging import get_logger, log_action

logger = get_logger(__name__)


@dataclass(slots=True)
class AuditRecord:
    event_type: str
    payload: dict[str, Any]
    actor: str = "system"
    source: str = "zentory"
    status: str = "recorded"
    audit_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "source": self.source,
            "status": self.status,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "mock": True,
        }


class AuditService:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    async def record(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.record_sync(payload)

    def record_sync(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = AuditRecord(
            event_type=str(payload.get("event_type", "unknown")),
            actor=str(payload.get("actor", "system")),
            source=str(payload.get("source", "zentory")),
            status=str(payload.get("status", "recorded")),
            payload=payload,
        )
        self._records.append(record)
        log_action(logger, "audit_record_created", **record.to_dict())
        return record.to_dict()

    def record_action_decision(
        self,
        *,
        action_id: str,
        action_type: str,
        decision: dict[str, Any],
    ) -> dict[str, Any]:
        return self.record_sync(
            {
                "event_type": "safety_action_evaluated",
                "action_id": action_id,
                "action_type": action_type,
                **decision,
                "mock": True,
            }
        )

    def list_records(self) -> list[dict[str, Any]]:
        return [record.to_dict() for record in self._records]

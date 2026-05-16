import pytest
from fastapi.testclient import TestClient

from zentory.actions.registry import ActionRegistry
from zentory.actions.schemas import Action
from zentory.agents.orchestrator import Orchestrator
from zentory.api.dependencies import get_orchestrator
from zentory.app.main import create_app
from zentory.core.enums import ActionStatus
from zentory.services.audit_service import AuditService
from zentory.services.retry_service import RetryConfig, RetryService
from zentory.services.safe_mode import SafeModeService


@pytest.mark.asyncio
async def test_retry_service_retries_until_success() -> None:
    attempts = {"count": 0}
    retry_service = RetryService(RetryConfig(attempts=3, delay_seconds=0))

    async def flaky_operation() -> dict[str, int]:
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise RuntimeError("mock external API temporary failure")
        return {"ok": attempts["count"]}

    result = await retry_service.run(flaky_operation, operation_name="mock_fetch_orders")

    assert result == {"ok": 2}
    assert attempts["count"] == 2


class FailingOrchestrator(Orchestrator):
    async def handle_event(self, event: dict) -> object:
        raise RuntimeError("mock webhook failure")


def test_telegram_webhook_error_does_not_crash_application() -> None:
    app = create_app()
    app.dependency_overrides[get_orchestrator] = lambda: FailingOrchestrator()
    client = TestClient(app)

    response = client.post("/telegram/webhook", json={"event_type": "mock_failure"})

    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert response.json()["source"] == "telegram_webhook"


@pytest.mark.asyncio
async def test_audit_log_is_created() -> None:
    audit_service = AuditService()

    record = await audit_service.record({"event_type": "agent_action", "mock": True})

    assert record["mock"] is True
    assert record["event_type"] == "agent_action"
    assert audit_service.list_records()[0]["audit_id"] == record["audit_id"]


def test_idempotency_prevents_duplicate_mock_execution() -> None:
    registry = ActionRegistry(safe_mode=SafeModeService(enabled=False))
    action = registry.register(Action(action_type="mock", title="Mock", description="Mock"))

    first = registry.execute_mock(action.action_id)
    second = registry.execute_mock(action.action_id)

    assert first.status == ActionStatus.EXECUTED
    assert second.status == ActionStatus.EXECUTED
    assert second.payload["idempotency_duplicate"] is True
    assert second.payload["mock_execution_count"] == 1

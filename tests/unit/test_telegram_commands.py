import pytest
from fastapi.testclient import TestClient

from zentory.app.main import create_app
from zentory.services.telegram_command_service import TelegramCommandService


def test_telegram_command_service_parses_approval_commands() -> None:
    service = TelegramCommandService()

    command = service.parse({"text": "/approve action-123", "chat_id": "42"})

    assert command.command == "/approve"
    assert command.event_type == "approve_action"
    assert command.action_id == "action-123"
    assert command.chat_id == "42"


def test_telegram_command_service_parses_sku_command() -> None:
    service = TelegramCommandService()

    command = service.parse({"text": "/sku ZNT-WB-001"})

    assert command.event_type == "sku_overview"
    assert command.payload["sku"] == "ZNT-WB-001"


@pytest.mark.parametrize(
    ("text", "event_type"),
    [
        ("/start", "control_start"),
        ("/help", "control_help"),
        ("/daily", "daily"),
        ("/alerts", "alerts"),
        ("/sku ZNT-WB-001", "sku_overview"),
        ("/plan", "plan"),
        ("/approve action-123", "approve_action"),
        ("/reject action-123", "reject_action"),
        ("/rollback action-123", "rollback_action"),
        ("/status", "control_status"),
    ],
)
def test_telegram_command_service_maps_minimal_commands(text: str, event_type: str) -> None:
    service = TelegramCommandService()

    command = service.parse({"text": text})

    assert command.event_type == event_type


def test_telegram_webhook_returns_managerial_sku_message() -> None:
    client = TestClient(create_app())

    response = client.post("/telegram/webhook", json={"text": "/sku ZNT-OZON-002"})

    assert response.status_code == 200
    body = response.json()
    assert body["mock"] is True
    assert body["event"]["event_type"] == "sku_overview"
    text = body["telegram_messages"][0]["text"]
    assert "Статус:" in text
    assert "Проблема:" in text
    assert "Рекомендация:" in text


def test_telegram_webhook_approve_command_uses_action_registry() -> None:
    client = TestClient(create_app())
    created = client.post("/telegram/webhook", json={"text": "/plan"}).json()
    action_id = created["decision"]["proposed_actions"][0]["action_id"]

    response = client.post("/telegram/webhook", json={"text": f"/approve {action_id}"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["action"]["status"] == "approved"

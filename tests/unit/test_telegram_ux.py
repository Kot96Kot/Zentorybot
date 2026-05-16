import pytest

from zentory.agents.orchestrator import Orchestrator
from zentory.integrations.telegram.commands import SUPPORTED_COMMANDS
from zentory.integrations.telegram.formatter import TelegramFormatter
from zentory.services.rollback_service import RollbackService
from zentory.services.telegram_command_service import TelegramCommandService


@pytest.mark.parametrize(
    ("text", "event_type"),
    [
        ("/start", "control_start"),
        ("/help", "control_help"),
        ("/daily", "daily"),
        ("/alerts", "alerts"),
        ("/sku WB-MOCK-1", "sku_overview"),
        ("/plan", "plan"),
        ("/approve action-1", "approve_action"),
        ("/reject action-1", "reject_action"),
        ("/rollback action-1", "rollback_action"),
        ("/status", "control_status"),
    ],
)
def test_minimal_commands_are_parsed(text: str, event_type: str) -> None:
    service = TelegramCommandService()

    command = service.parse({"text": text, "chat_id": "manager"})

    assert command.event_type == event_type
    assert command.command in SUPPORTED_COMMANDS
    assert command.chat_id == "manager"


def test_sku_command_extracts_sku_without_agent_choice() -> None:
    service = TelegramCommandService()

    command = service.parse({"text": "/sku WB-123"})

    assert command.event_type == "sku_overview"
    assert command.sku == "WB-123"
    assert command.payload["sku"] == "WB-123"


@pytest.mark.asyncio
async def test_orchestrator_returns_daily_manager_card() -> None:
    orchestrator = Orchestrator()
    formatter = TelegramFormatter()

    decision = await orchestrator.handle_event({"event_type": "daily", "payload": {}, "mock": True})
    text = formatter.format_decision(decision)

    assert "Статус:" in text
    assert "Проблема:" in text
    assert "Причина:" in text
    assert "Рекомендация:" in text
    assert "Риск:" in text
    assert "отчет за вчера" in text


@pytest.mark.asyncio
async def test_orchestrator_returns_sku_overview_card() -> None:
    orchestrator = Orchestrator()
    formatter = TelegramFormatter()

    decision = await orchestrator.handle_event(
        {"event_type": "sku_overview", "payload": {"sku": "WB-777"}, "mock": True}
    )
    text = formatter.format_decision(decision)

    assert "SKU WB-777" in text
    assert "остат" in text
    assert "реклама" in text
    assert "отзывы" in text


def test_formatter_help_hides_manual_agent_commands() -> None:
    text = TelegramFormatter().format_help()

    assert "/daily" in text
    assert "/sku <sku>" in text
    assert "/approve" in text
    assert "/agents" not in text
    assert "/ads_today" not in text


def test_rollback_service_returns_mock_unavailable_result() -> None:
    result = RollbackService().rollback("missing-action")
    text = TelegramFormatter().format_rollback_result(result)

    assert result["status"] == "rollback unavailable"
    assert "Статус:" in text
    assert "rollback unavailable" in text

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from zentory.actions.registry import ActionRegistry
from zentory.agents.orchestrator import Orchestrator
from zentory.api.dependencies import (
    get_action_registry,
    get_orchestrator,
    get_rollback_service,
    get_telegram_client,
    get_telegram_command_service,
    get_telegram_formatter,
)
from zentory.core.enums import EventSource
from zentory.core.errors import ActionNotFoundError, handle_internal_error
from zentory.core.logging import get_logger, log_action
from zentory.integrations.telegram.client import TelegramClient
from zentory.integrations.telegram.formatter import TelegramFormatter
from zentory.services.rollback_service import RollbackService
from zentory.services.telegram_command_service import TelegramCommandService

router = APIRouter(prefix="/telegram", tags=["telegram"])
logger = get_logger(__name__)

OrchestratorDependency = Annotated[Orchestrator, Depends(get_orchestrator)]
CommandServiceDependency = Annotated[TelegramCommandService, Depends(get_telegram_command_service)]
TelegramClientDependency = Annotated[TelegramClient, Depends(get_telegram_client)]
TelegramFormatterDependency = Annotated[TelegramFormatter, Depends(get_telegram_formatter)]
ActionRegistryDependency = Annotated[ActionRegistry, Depends(get_action_registry)]
RollbackServiceDependency = Annotated[RollbackService, Depends(get_rollback_service)]


@router.post("/webhook")
async def telegram_webhook(
    payload: dict[str, Any],
    orchestrator: OrchestratorDependency,
    command_service: CommandServiceDependency,
    telegram_client: TelegramClientDependency,
    formatter: TelegramFormatterDependency,
    registry: ActionRegistryDependency,
    rollback_service: RollbackServiceDependency,
) -> dict[str, Any]:
    event_type = str(payload.get("event_type", "unknown"))
    try:
        command = command_service.parse(payload)
        event_type = command.event_type
        log_action(
            logger,
            "telegram_webhook_received",
            command=command.command,
            event_type=command.event_type,
            mock=True,
        )
        if command.error == "missing_argument":
            text = formatter.format_control_message(command.event_type, command.payload)
            sent = await telegram_client.send_telegram_message(command.chat_id, text)
            return {
                "mock": True,
                "status": "error",
                "event_type": command.event_type,
                "proposed_actions": [],
                "command": command.command,
                "telegram_messages": [sent],
            }
        if command.event_type in {"approve_action", "reject_action"}:
            return await _handle_approval_command(command, telegram_client, formatter, registry)
        if command.event_type == "rollback_action":
            return await _handle_rollback_command(
                command, telegram_client, formatter, rollback_service
            )

        event = {
            "source": EventSource.TELEGRAM,
            "event_type": command.event_type,
            "payload": command.payload,
            "mock": True,
        }
        decision = await orchestrator.handle_event(event)
        messages = formatter.format_messages(decision)
        for message in messages:
            if "card" in message:
                await telegram_client.send_action_card(command.chat_id, message["card"])
            elif "buttons" in message:
                await telegram_client.send_action_card(command.chat_id, message)
            else:
                await telegram_client.send_telegram_message(command.chat_id, message["text"])
        return {
            "mock": True,
            "status": "ok",
            "event_type": command.event_type,
            "proposed_actions": [
                action.model_dump(mode="json") for action in decision.proposed_actions
            ],
            "command": command.command,
            "event": event,
            "decision": decision.model_dump(mode="json"),
            "telegram_messages": messages,
        }
    except Exception as exc:  # noqa: BLE001 - webhook must not crash the app
        error_payload = handle_internal_error(exc, source="telegram_webhook")
        error_payload["event_type"] = event_type
        error_payload["proposed_actions"] = []
        return error_payload


async def _handle_approval_command(
    command: Any,
    telegram_client: TelegramClient,
    formatter: TelegramFormatter,
    registry: ActionRegistry,
) -> dict[str, Any]:
    if command.action_id is None:
        return {
            "mock": True,
            "status": "error",
            "event_type": command.event_type,
            "proposed_actions": [],
            "detail": "action_id is required",
        }
    try:
        approved = command.event_type == "approve_action"
        action = (
            registry.approve(command.action_id) if approved else registry.reject(command.action_id)
        )
        text = formatter.format_approval_result(action, approved=approved)
        sent = await telegram_client.send_telegram_message(command.chat_id, text)
        return {
            "mock": True,
            "status": "ok",
            "event_type": command.event_type,
            "proposed_actions": [],
            "action": action.model_dump(mode="json"),
            "telegram_messages": [sent],
        }
    except ActionNotFoundError as exc:
        payload = handle_internal_error(exc, source="telegram_webhook")
        await telegram_client.send_telegram_message(command.chat_id, payload["detail"])
        payload["event_type"] = command.event_type
        payload["proposed_actions"] = []
        return payload


async def _handle_rollback_command(
    command: Any,
    telegram_client: TelegramClient,
    formatter: TelegramFormatter,
    rollback_service: RollbackService,
) -> dict[str, Any]:
    if command.action_id is None:
        text = formatter.format_control_message(
            command.event_type, {"missing_argument": "action_id"}
        )
        sent = await telegram_client.send_telegram_message(command.chat_id, text)
        return {
            "mock": True,
            "status": "error",
            "event_type": command.event_type,
            "proposed_actions": [],
            "telegram_messages": [sent],
        }
    result = rollback_service.rollback(command.action_id)
    text = formatter.format_rollback_result(result)
    sent = await telegram_client.send_telegram_message(command.chat_id, text)
    return {
        "mock": True,
        "status": result["status"],
        "event_type": command.event_type,
        "proposed_actions": [],
        "rollback": result,
        "telegram_messages": [sent],
    }

from dataclasses import dataclass, field
from typing import Any

from zentory.integrations.telegram.commands import COMMANDS_BY_NAME, SUPPORTED_COMMANDS


@dataclass(frozen=True, slots=True)
class TelegramCommand:
    command: str
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    chat_id: str = "mock_chat"
    action_id: str | None = None
    sku: str | None = None
    error: str | None = None


class TelegramCommandService:
    def parse(self, payload: dict[str, Any]) -> TelegramCommand:
        text = self._extract_text(payload)
        parts = text.split()
        command = (
            parts[0] if parts and parts[0].startswith("/") else str(payload.get("command", ""))
        )
        spec = COMMANDS_BY_NAME.get(command)
        enriched_payload = dict(payload)
        chat_id = self._extract_chat_id(payload)

        if spec is None:
            payload_event_type = payload.get("event_type")
            if not command and payload_event_type is not None:
                return TelegramCommand(
                    command="event_payload",
                    event_type=str(payload_event_type),
                    payload=enriched_payload,
                    chat_id=chat_id,
                )
            return TelegramCommand(
                command=command or "unknown",
                event_type="control_help",
                payload={**enriched_payload, "supported_commands": SUPPORTED_COMMANDS},
                chat_id=chat_id,
                error="unsupported_command",
            )

        argument = parts[1] if len(parts) > 1 else None
        if argument is None and spec.argument_name is not None:
            raw_argument = payload.get(spec.argument_name)
            argument = str(raw_argument) if raw_argument is not None else None
        action_id = argument if spec.argument_name == "action_id" else None
        sku = argument if spec.argument_name == "sku" else None
        metric = argument if spec.argument_name == "metric" else None
        if spec.requires_argument and argument is None:
            return TelegramCommand(
                command=command,
                event_type=spec.event_type,
                payload={
                    **enriched_payload,
                    "missing_argument": spec.argument_name,
                    "supported_commands": SUPPORTED_COMMANDS,
                },
                chat_id=chat_id,
                error="missing_argument",
            )
        if action_id is not None:
            enriched_payload["action_id"] = action_id
        if sku is not None:
            enriched_payload["sku"] = sku
        if metric is not None:
            enriched_payload["metric"] = metric

        return TelegramCommand(
            command=command,
            event_type=spec.event_type,
            payload=enriched_payload,
            chat_id=chat_id,
            action_id=action_id,
            sku=sku,
        )

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        message = payload.get("message", {})
        message_text = message.get("text") if isinstance(message, dict) else ""
        return str(payload.get("text") or message_text or "").strip()

    @staticmethod
    def _extract_chat_id(payload: dict[str, Any]) -> str:
        message = payload.get("message", {})
        chat = message.get("chat", {}) if isinstance(message, dict) else {}
        return str(payload.get("chat_id") or chat.get("id") or "mock_chat")

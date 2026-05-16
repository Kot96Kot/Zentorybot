from typing import Any


class TelegramClient:
    def __init__(self) -> None:
        self.sent_messages: list[dict[str, Any]] = []

    async def send_telegram_message(self, chat_id: str, text: str) -> dict[str, Any]:
        message = {"mock": True, "chat_id": chat_id, "text": text, "status": "not_sent"}
        self.sent_messages.append(message)
        return message

    async def send_action_card(self, chat_id: str, card: dict[str, Any]) -> dict[str, Any]:
        message = {"mock": True, "chat_id": chat_id, "card": card, "status": "not_sent"}
        self.sent_messages.append(message)
        return message

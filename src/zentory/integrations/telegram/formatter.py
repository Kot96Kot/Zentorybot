from typing import Any

from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode
from zentory.decision.engine import DecisionResult
from zentory.integrations.telegram.commands import COMMAND_SPECS


def format_daily_digest(report: dict) -> str:
    deviations = ", ".join(report.get("deviations", [])) or "критичных отклонений нет"
    return (
        "📊 Daily / вчера\n"
        "Статус: mock-отчет готов\n"
        f"Проблема: {deviations}\n"
        "Причина: данные собраны из mock-модулей продаж, рекламы и остатков\n"
        "Рекомендация: проверьте действия с кнопками approval\n"
        "Риск: LOW"
    )


class TelegramFormatter:
    def format_control_message(self, event_type: str, payload: dict[str, Any] | None = None) -> str:
        payload = payload or {}
        if event_type == "control_start":
            return self._manager_message(
                status="Zentorybot запущен",
                problem="ручной выбор агентов не нужен",
                reason="Orchestrator сам маршрутизирует команды в нужный модуль",
                recommendation="используйте /daily, /alerts, /sku <sku>, /plan или /status",
                risk="LOW",
            )
        if event_type == "control_status":
            return self._manager_message(
                status="mock-ready; Safety Core включен",
                problem="реальные Telegram и marketplace API не подключены",
                reason="система работает в безопасном mock-режиме",
                recommendation="проверяйте proposed actions через /approve или /reject",
                risk="LOW",
            )
        if payload.get("missing_argument"):
            return self._manager_message(
                status="нужен аргумент команды",
                problem=f"не передан {payload['missing_argument']}",
                reason="команда требует идентификатор",
                recommendation="пример: /sku WB-MOCK-1 или /approve action_id",
                risk="LOW",
            )
        return self.format_help()

    def format_help(self) -> str:
        command_lines = []
        for spec in COMMAND_SPECS:
            command = spec.name.value
            if spec.argument_name is not None:
                command = f"{command} <{spec.argument_name}>"
            command_lines.append(f"• {command} — {spec.description}")
        return self._manager_message(
            status="доступен минимальный Telegram UX",
            problem="лишние команды агентов скрыты",
            reason="пользователь пишет бизнес-команду, Orchestrator выбирает модуль",
            recommendation="\n".join(command_lines),
            risk="LOW",
        )

    def format_decision(self, decision: DecisionResult) -> str:
        if decision.proposed_actions:
            primary = decision.proposed_actions[0]
            response = primary.payload.get("telegram_response")
            if isinstance(response, dict):
                return self.format_manager_card(response)
        return self._manager_message(
            status="команда обработана",
            problem="нет предложенных действий",
            reason="mock-модули не нашли задач для команды",
            recommendation="запросите /daily, /alerts, /sku <sku> или /plan",
            risk=str(decision.risk_level),
        )

    def format_manager_card(self, card: dict[str, Any]) -> str:
        buttons = card.get("buttons") or []
        button_text = " ".join(
            button.get("command", button.get("text", ""))
            for button in buttons
            if isinstance(button, dict)
        )
        lines = [
            f"Статус: {card.get('status', 'mock-ready')}",
            f"Проблема: {card.get('problem', 'нет критичных проблем')}",
            f"Причина: {card.get('reason', 'mock-анализ')}",
            f"Рекомендация: {card.get('recommendation', 'наблюдать')}",
            f"Риск: {card.get('risk', 'LOW')}",
        ]
        if button_text:
            lines.append(f"Кнопки: {button_text}")
        return "\n".join(lines)

    def format_action_card(self, action: Action) -> dict[str, Any]:
        card = action.payload.get("telegram_response")
        text = self.format_manager_card(card) if isinstance(card, dict) else self._manager_message(
            status="нужен approval",
            problem=action.title,
            reason=action.description,
            recommendation=f"подтвердить или отклонить action_id={action.action_id}",
            risk=str(action.risk_level),
        )
        return {
            "text": text,
            "buttons": [
                {"text": "Approve", "command": f"/approve {action.action_id}"},
                {"text": "Reject", "command": f"/reject {action.action_id}"},
            ],
            "mock": True,
        }

    def format_approval_result(self, action: Action, *, approved: bool) -> str:
        return self._manager_message(
            status="action approved" if approved else "action rejected",
            problem=action.title,
            reason="решение получено из Telegram-команды",
            recommendation="следите за /status и /alerts",
            risk=str(action.risk_level),
        )

    def format_rollback_result(self, result: dict[str, Any]) -> str:
        return self._manager_message(
            status=str(result.get("status", "rollback unavailable")),
            problem=str(result.get("problem", "нет rollback-плана")),
            reason=str(result.get("reason", "mock rollback service")),
            recommendation=str(result.get("recommendation", "проверьте action_id")),
            risk=str(result.get("risk", "MEDIUM")),
        )

    def format_messages(self, decision: DecisionResult) -> list[dict[str, Any]]:
        messages = [{"text": self.format_decision(decision), "mock": True}]
        approval_cards = [
            self.format_action_card(action)
            for action in decision.proposed_actions
            if action.approval_mode != ApprovalMode.NONE
        ]
        return messages + approval_cards

    @staticmethod
    def _manager_message(
        *, status: str, problem: str, reason: str, recommendation: str, risk: str
    ) -> str:
        return (
            f"Статус: {status}\n"
            f"Проблема: {problem}\n"
            f"Причина: {reason}\n"
            f"Рекомендация: {recommendation}\n"
            f"Риск: {risk}"
        )

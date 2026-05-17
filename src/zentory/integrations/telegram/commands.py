from dataclasses import dataclass
from enum import StrEnum


class TelegramCommandName(StrEnum):
    START = "/start"
    HELP = "/help"
    DAILY = "/daily"
    ALERTS = "/alerts"
    SKU = "/sku"
    PLAN = "/plan"
    APPROVE = "/approve"
    REJECT = "/reject"
    ROLLBACK = "/rollback"
    STATUS = "/status"


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: TelegramCommandName
    event_type: str
    description: str
    requires_argument: bool = False
    argument_name: str | None = None


COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(TelegramCommandName.START, "control_start", "Запустить Zentorybot"),
    CommandSpec(TelegramCommandName.HELP, "control_help", "Показать короткую справку"),
    CommandSpec(
        TelegramCommandName.DAILY,
        "daily",
        "Сводка дня: продажи, остатки, реклама, отзывы, алерты",
    ),
    CommandSpec(
        TelegramCommandName.ALERTS,
        "alerts",
        "Critical/warning сигналы и pending approvals",
    ),
    CommandSpec(
        TelegramCommandName.SKU,
        "sku_overview",
        "Единая карточка SKU: продажи, остатки, реклама, отзывы, конкуренты, прогноз",
        requires_argument=True,
        argument_name="sku",
    ),
    CommandSpec(TelegramCommandName.PLAN, "plan", "План действий на день"),
    CommandSpec(
        TelegramCommandName.APPROVE,
        "approve_action",
        "Подтвердить предложенное действие",
        requires_argument=True,
        argument_name="action_id",
    ),
    CommandSpec(
        TelegramCommandName.REJECT,
        "reject_action",
        "Отклонить предложенное действие",
        requires_argument=True,
        argument_name="action_id",
    ),
    CommandSpec(
        TelegramCommandName.ROLLBACK,
        "rollback_action",
        "Откатить действие, если rollback доступен",
        requires_argument=True,
        argument_name="action_id",
    ),
    CommandSpec(
        TelegramCommandName.STATUS,
        "control_status",
        "Safety mode, agents, mock mode, pending actions",
    ),
)

COMMANDS_BY_NAME = {spec.name.value: spec for spec in COMMAND_SPECS}
SUPPORTED_COMMANDS = tuple(spec.name.value for spec in COMMAND_SPECS)

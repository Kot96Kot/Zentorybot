from dataclasses import dataclass
from enum import StrEnum


class TelegramCommandName(StrEnum):
    START = "/start"
    HELP = "/help"
    DAILY = "/daily"
    ALERTS = "/alerts"
    SKU = "/sku"
    ABC = "/abc"
    FORECAST = "/forecast"
    FORECAST_SKU = "/forecast_sku"
    STOCK_RISKS = "/stock_risks"
    REPLENISHMENT = "/replenishment"
    WAREHOUSES = "/warehouses"
    CONTENT_SKU = "/content_sku"
    CTR_TEST = "/ctr_test"
    CONTENT_BRIEF = "/content_brief"
    FINANCE_CHECK = "/finance_check"
    PNL_CHECK = "/pnl_check"
    UNIT = "/unit"
    PLAN = "/plan"
    APPROVE = "/approve"
    REJECT = "/reject"
    ROLLBACK = "/rollback"
    ACTION_RESULT = "/action_result"
    LEARNING = "/learning"
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
    CommandSpec(
        TelegramCommandName.ABC,
        "abc",
        "ABC-анализ по revenue, profit или sales_qty",
        argument_name="metric",
    ),
    CommandSpec(
        TelegramCommandName.FORECAST,
        "forecast",
        "Прогноз продаж и остатков на 30/60/90 дней",
    ),
    CommandSpec(
        TelegramCommandName.FORECAST_SKU,
        "forecast_sku",
        "Прогноз остатков по одному SKU",
        requires_argument=True,
        argument_name="sku",
    ),
    CommandSpec(
        TelegramCommandName.STOCK_RISKS,
        "stock_risks",
        "Риски остатков и out-of-stock по складам",
    ),
    CommandSpec(
        TelegramCommandName.REPLENISHMENT,
        "replenishment",
        "План отгрузок и подсортов",
    ),
    CommandSpec(
        TelegramCommandName.WAREHOUSES,
        "warehouses",
        "Локализация и рекомендации по складам",
    ),
    CommandSpec(
        TelegramCommandName.CONTENT_SKU,
        "content_sku",
        "Content CTR Factory по одному SKU",
        requires_argument=True,
        argument_name="sku",
    ),
    CommandSpec(
        TelegramCommandName.CTR_TEST,
        "ctr_test",
        "План CTR-теста для главного фото",
    ),
    CommandSpec(
        TelegramCommandName.CONTENT_BRIEF,
        "content_brief",
        "Бриф контента и CTR-гипотезы",
    ),
    CommandSpec(
        TelegramCommandName.FINANCE_CHECK,
        "finance_check",
        "Проверка финансовых расчетов и аномалий",
    ),
    CommandSpec(
        TelegramCommandName.PNL_CHECK,
        "pnl_check",
        "Сверка PnL по SKU",
    ),
    CommandSpec(
        TelegramCommandName.UNIT,
        "unit",
        "Unit profit по одному SKU",
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
        TelegramCommandName.ACTION_RESULT,
        "action_result",
        "Показать результат действия и learning status",
        requires_argument=True,
        argument_name="action_id",
    ),
    CommandSpec(
        TelegramCommandName.LEARNING,
        "learning",
        "История обучения по SKU",
        requires_argument=True,
        argument_name="sku",
    ),
    CommandSpec(
        TelegramCommandName.STATUS,
        "control_status",
        "Safety mode, agents, mock mode, pending actions",
    ),
)

COMMANDS_BY_NAME = {spec.name.value: spec for spec in COMMAND_SPECS}
SUPPORTED_COMMANDS = tuple(spec.name.value for spec in COMMAND_SPECS)

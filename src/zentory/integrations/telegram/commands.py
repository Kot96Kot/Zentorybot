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
    ABC = "/abc"
    FORECAST = "/forecast"
    FORECAST_SKU = "/forecast_sku"
    STOCK_FORECAST = "/stock_forecast"
    SEASONALITY = "/seasonality"


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
    CommandSpec(TelegramCommandName.DAILY, "daily", "Отчет за вчера и ключевые отклонения"),
    CommandSpec(TelegramCommandName.ALERTS, "alerts", "Только ситуации, требующие внимания"),
    CommandSpec(
        TelegramCommandName.SKU,
        "sku_overview",
        "Карточка SKU: продажи, остатки, реклама, отзывы, рекомендации",
        requires_argument=True,
        argument_name="sku",
    ),
    CommandSpec(TelegramCommandName.PLAN, "plan", "План действий на сегодня"),
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
    CommandSpec(TelegramCommandName.STATUS, "control_status", "Статус агентов и safety mode"),
    CommandSpec(
        TelegramCommandName.ABC,
        "abc",
        "ABC-анализ SKU по revenue/profit/sales_qty",
        argument_name="metric",
    ),
    CommandSpec(TelegramCommandName.FORECAST, "forecast", "Forecast продаж и остатков"),
    CommandSpec(
        TelegramCommandName.FORECAST_SKU,
        "forecast_sku",
        "Forecast по одному SKU",
        requires_argument=True,
        argument_name="sku",
    ),
    CommandSpec(TelegramCommandName.STOCK_FORECAST, "stock_forecast", "Прогноз остатков"),
    CommandSpec(TelegramCommandName.SEASONALITY, "seasonality", "Сезонные коэффициенты"),
)

COMMANDS_BY_NAME = {spec.name.value: spec for spec in COMMAND_SPECS}
SUPPORTED_COMMANDS = tuple(spec.name.value for spec in COMMAND_SPECS)

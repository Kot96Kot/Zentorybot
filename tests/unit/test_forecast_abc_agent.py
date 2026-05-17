import asyncio

from zentory.agents.forecast_abc_agent import ForecastABCAgent
from zentory.api.routers.analytics import (
    abc_by_metric,
    abc_default,
    forecast,
    forecast_sku,
    stock_forecast,
)
from zentory.integrations.telegram.commands import SUPPORTED_COMMANDS
from zentory.schemas.abc import ABCMetric
from zentory.services.forecast_service import ForecastService
from zentory.services.telegram_command_service import TelegramCommandService


def test_forecast_abc_agent_returns_abc_action_with_self_checked_mock_data() -> None:
    actions = asyncio.run(ForecastABCAgent().propose_actions({"event_type": "abc", "payload": {}}))

    assert actions
    assert actions[0].action_type == "abc"
    assert actions[0].payload["mock"] is True
    card = actions[0].payload["telegram_response"]
    assert "ABC-анализ" in card["status"]
    assert card["top_10"]
    assert card["class_summary"]


def test_forecast_abc_agent_returns_sku_forecast_card() -> None:
    actions = asyncio.run(
        ForecastABCAgent().propose_actions(
            {"event_type": "forecast_sku", "payload": {"sku": "ZNT-COS-001"}}
        )
    )

    card = actions[0].payload["telegram_response"]
    assert card["forecast"]["sku"] == "ZNT-COS-001"
    assert card["forecast"]["forecast_sales_30"] > 0
    assert card["forecast"]["seasonality_coefficient"] > 0
    assert card["forecast"]["trend_coefficient"] > 0
    assert card["self_check"] == "passed"


def test_forecast_service_aggregates_stock_by_warehouse_and_region() -> None:
    item = ForecastService().load_aggregated_skus()[0]

    assert item.stock_by_warehouse
    assert item.stock_by_region
    assert item.total_stock == sum(item.stock_by_warehouse.values())
    assert item.mock is True


def test_forecast_telegram_commands_are_supported_and_parse_arguments() -> None:
    command = TelegramCommandService().parse({"text": "/abc profit", "chat_id": "1"})
    sku_command = TelegramCommandService().parse({"text": "/forecast_sku ZNT-COS-001"})

    assert "/abc" in SUPPORTED_COMMANDS
    assert "/forecast" in SUPPORTED_COMMANDS
    assert "/stock_forecast" in SUPPORTED_COMMANDS
    assert "/seasonality" in SUPPORTED_COMMANDS
    assert command.event_type == "abc"
    assert command.payload["metric"] == "profit"
    assert sku_command.event_type == "forecast_sku"
    assert sku_command.payload["sku"] == "ZNT-COS-001"


def test_analytics_endpoints_return_json_serializable_mock_dicts() -> None:
    service = ForecastService()

    responses = [
        asyncio.run(abc_default(service)),
        asyncio.run(abc_by_metric(ABCMetric.PROFIT, service)),
        asyncio.run(forecast(service)),
        asyncio.run(forecast_sku("ZNT-COS-001", service)),
        asyncio.run(stock_forecast(service)),
    ]

    assert all(isinstance(response, dict) for response in responses)
    assert all(response.get("mock_mode") is True for response in responses)
    assert responses[3]["forecast"]["sku"] == "ZNT-COS-001"

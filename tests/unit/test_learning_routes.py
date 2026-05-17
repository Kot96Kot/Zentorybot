import asyncio

from zentory.api.routers.learning import action_result, learning_actions, learning_sku
from zentory.schemas.learning import ActionResultRequest
from zentory.services.action_result_service import ActionResultService
from zentory.services.telegram_command_service import TelegramCommandService


def test_learning_routes_record_and_list_actions() -> None:
    service = ActionResultService()
    request = ActionResultRequest(
        action_id="route-act-1",
        agent="ads_agent",
        sku="SKU-ROUTE",
        recommendation="снизить ставку на 15%",
        expected_effect="снизить ДРР",
        metric_name="ДРР",
        metric_before=18.0,
        metric_after=12.0,
    )

    posted = asyncio.run(action_result(request, service))
    all_actions = asyncio.run(learning_actions(service))
    sku_actions = asyncio.run(learning_sku("SKU-ROUTE", service))

    assert posted["mock_mode"] is True
    assert posted["action"]["status"] == "SUCCESS"
    assert all_actions["summary"]["successful_actions"] == 1
    assert sku_actions["sku"] == "SKU-ROUTE"
    assert sku_actions["actions"][0]["action_id"] == "route-act-1"


def test_learning_telegram_commands_are_parsed() -> None:
    service = TelegramCommandService()

    action_result_command = service.parse({"text": "/action_result route-act-1"})
    learning_command = service.parse({"text": "/learning SKU-ROUTE"})

    assert action_result_command.event_type == "action_result"
    assert action_result_command.action_id == "route-act-1"
    assert learning_command.event_type == "learning"
    assert learning_command.sku == "SKU-ROUTE"

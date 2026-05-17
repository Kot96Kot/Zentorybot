import asyncio

from zentory.api.routers.finance import finance_check, finance_pnl, finance_unit
from zentory.services.finance_checker_service import FinanceCheckerService
from zentory.services.telegram_command_service import TelegramCommandService


def test_finance_routes_return_mock_contracts() -> None:
    service = FinanceCheckerService()

    check = asyncio.run(finance_check(service))
    pnl = asyncio.run(finance_pnl(service))
    unit = asyncio.run(finance_unit("ZNT-PROFIT-001", service))

    assert check["mock_mode"] is True
    assert check["issues"]
    assert pnl["units"]
    assert unit["unit"]["sku"] == "ZNT-PROFIT-001"


def test_finance_telegram_commands_are_parsed() -> None:
    service = TelegramCommandService()

    finance = service.parse({"text": "/finance_check"})
    pnl = service.parse({"text": "/pnl_check"})
    unit = service.parse({"text": "/unit ZNT-PROFIT-001"})

    assert finance.event_type == "finance_check"
    assert pnl.event_type == "pnl_check"
    assert unit.event_type == "unit"
    assert unit.payload["sku"] == "ZNT-PROFIT-001"

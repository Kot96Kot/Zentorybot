import pytest

from zentory.agents.inventory_agent import InventoryAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.inventory import InventoryPriority, InventoryStatus
from zentory.services.inventory_service import InventoryService


@pytest.mark.asyncio
async def test_inventory_agent_returns_stock_summary_for_stocks_command() -> None:
    agent = InventoryAgent()

    analysis = await agent.analyze({"event_type": "stocks", "payload": {"mock": True}})

    assert analysis["mock"] is True
    assert analysis["inventory"]["reports"]
    assert analysis["inventory"]["out_of_stock_risks"]
    assert analysis["inventory"]["slow_movers"]


@pytest.mark.asyncio
async def test_inventory_agent_filters_by_sku_and_creates_replenishment_actions() -> None:
    agent = InventoryAgent()

    actions = await agent.propose_actions(
        {"event_type": "sku_stock", "payload": {"sku": "ZNT-WB-001"}}
    )

    assert actions
    assert all(action.payload["report"]["sku"] == "ZNT-WB-001" for action in actions)
    assert any("shipment" in action.action_type for action in actions)
    assert any("redistribution" in action.action_type for action in actions)
    assert any(action.action_type == "inventory_ads_alert" for action in actions)
    assert any(action.risk_level == RiskLevel.HIGH for action in actions)


def test_inventory_service_marks_critical_when_coverage_less_than_7_days() -> None:
    service = InventoryService()

    report = service.analyze(sku="ZNT-WB-001").reports[0]

    assert report.status == InventoryStatus.CRITICAL
    assert report.priority == InventoryPriority.CRITICAL
    assert report.out_of_stock_risk is True
    assert report.telegram_alert is not None
    assert report.alerts_for_ads_agent


def test_inventory_service_marks_slow_mover_and_excess() -> None:
    service = InventoryService()

    report = service.analyze(sku="ZNT-YM-003").reports[0]

    assert report.status == InventoryStatus.SLOW_MOVER
    assert report.slow_mover is True
    assert report.excess_stock is True

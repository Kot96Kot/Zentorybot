import pytest

from zentory.agents.platform_modules_agent import PlatformModulesAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.services.platform_modules_service import PlatformModulesService


def test_platform_modules_snapshot_contains_all_clean_modules() -> None:
    snapshot = PlatformModulesService().build_snapshot()

    assert snapshot.forecast_abc.mock is True
    assert snapshot.forecast_abc.summary["A"] == 1
    assert snapshot.supply_localization.items
    assert snapshot.supply_localization.blocked_actions
    assert snapshot.content_ctr_factory.experiments[0].target_ctr_percent > 2
    assert snapshot.finance_checker.total_contribution_profit > 0
    assert snapshot.learning_loop.signals
    assert {contract.name for contract in snapshot.data_contracts.contracts} == {
        "sku_daily_snapshot",
        "action_recommendation",
    }


def test_platform_modules_manager_summary_is_compact() -> None:
    summary = PlatformModulesService().build_snapshot().to_manager_summary()

    assert summary == {
        "forecast_items": 3,
        "supply_moves": 2,
        "content_experiments": 1,
        "finance_checks": 2,
        "learning_signals": 2,
        "contracts": ["sku_daily_snapshot", "action_recommendation"],
    }


@pytest.mark.asyncio
async def test_platform_modules_agent_returns_safe_advisory_action() -> None:
    action = (await PlatformModulesAgent().propose_actions({"event_type": "platform_modules"}))[0]

    assert action.agent_name == "platform_modules"
    assert action.action_type == "platform_modules_snapshot"
    assert action.risk_level == RiskLevel.MEDIUM
    assert action.approval_mode == ApprovalMode.SOFT_APPROVAL
    assert action.rollback_available is False
    assert action.payload["mock"] is True
    assert action.evidence

import pytest

from zentory.agents.team import (
    AICFO,
    AICOO,
    AIAdsManager,
    AIAnalyst,
    AIContentDirector,
    AIMarketplaceManager,
    AISupplyManager,
)
from zentory.schemas.team import TeamRoleName


def test_ai_team_roles_describe_responsibilities_and_approval_rules() -> None:
    roles = [
        AIMarketplaceManager(),
        AIAnalyst(),
        AIAdsManager(),
        AIContentDirector(),
        AICFO(),
        AISupplyManager(),
        AICOO(),
    ]

    assert {role.describe().role for role in roles} == {
        TeamRoleName.MARKETPLACE_MANAGER,
        TeamRoleName.ANALYST,
        TeamRoleName.ADS_MANAGER,
        TeamRoleName.CONTENT_DIRECTOR,
        TeamRoleName.CFO,
        TeamRoleName.SUPPLY_MANAGER,
        TeamRoleName.COO,
    }
    for role in roles:
        definition = role.describe()
        assert definition.included_agents
        assert definition.telegram_commands
        assert definition.no_approval_actions
        assert definition.approval_required_actions
        assert definition.mock is True


@pytest.mark.asyncio
async def test_ai_cfo_coordinates_existing_agents_and_returns_clear_result() -> None:
    role = AICFO()

    result = await role.coordinate({"event_type": "promo_check", "payload": {"mock": True}})

    assert result.role == TeamRoleName.CFO
    assert result.agent_results
    assert result.actions_count > 0
    assert result.recommendations
    assert result.next_telegram_commands == ["/unit", "/promo_check", "/promo_list"]


@pytest.mark.asyncio
async def test_ai_supply_manager_aggregates_inventory_agent() -> None:
    role = AISupplyManager()

    result = await role.coordinate({"event_type": "stock_risks", "payload": {"mock": True}})

    assert result.role == TeamRoleName.SUPPLY_MANAGER
    assert result.agent_results[0]["agent"] == "inventory"
    assert result.actions_count > 0
    assert result.mock is True

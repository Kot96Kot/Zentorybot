from zentory.agents.inventory_agent import InventoryAgent
from zentory.agents.team.base import BaseTeamRole
from zentory.schemas.team import TeamRoleDefinition, TeamRoleName


class AISupplyManager(BaseTeamRole):
    definition = TeamRoleDefinition(
        role=TeamRoleName.SUPPLY_MANAGER,
        responsibility=(
            "Следит за остатками, out-of-stock рисками, поставками и подсортами по складам."
        ),
        input_data=["stocks", "sales velocity", "warehouse stock", "transit", "supply plan"],
        output_result=["OOS risk list", "replenishment plan", "warehouse redistribution tasks"],
        included_agents=["InventoryAgent"],
        telegram_commands=["/stocks", "/stock_risks", "/replenishment"],
        no_approval_actions=["создать stock alert", "рассчитать покрытие", "найти slow mover"],
        approval_required_actions=[
            "создать поставку",
            "перераспределить склад",
            "изменить рекламный статус SKU",
        ],
    )

    def __init__(self) -> None:
        super().__init__([InventoryAgent()])

from zentory.agents.analytics_agent import AnalyticsAgent
from zentory.agents.sales_plan_agent import SalesPlanAgent
from zentory.agents.team.base import BaseTeamRole
from zentory.schemas.team import TeamRoleDefinition, TeamRoleName


class AIMarketplaceManager(BaseTeamRole):
    definition = TeamRoleDefinition(
        role=TeamRoleName.MARKETPLACE_MANAGER,
        responsibility=(
            "Единый координатор ежедневной операционки маркетплейсов и приоритетов роста."
        ),
        input_data=["sales plan", "daily analytics", "alerts", "owner goals"],
        output_result=["daily action plan", "приоритеты SKU", "сводка для владельца"],
        included_agents=["SalesPlanAgent", "AnalyticsAgent"],
        telegram_commands=["/daily", "/sales_plan", "/alerts", "/status"],
        no_approval_actions=["собрать digest", "показать статус", "создать задачу на анализ"],
        approval_required_actions=[
            "изменить бюджет",
            "утвердить план продаж",
            "применить risky action",
        ],
    )

    def __init__(self) -> None:
        super().__init__([SalesPlanAgent(), AnalyticsAgent()])

from zentory.agents.analytics_agent import AnalyticsAgent
from zentory.agents.category_agent import CategoryAgent
from zentory.agents.competitor_agent import CompetitorAgent
from zentory.agents.team.base import BaseTeamRole
from zentory.schemas.team import TeamRoleDefinition, TeamRoleName


class AIAnalyst(BaseTeamRole):
    definition = TeamRoleDefinition(
        role=TeamRoleName.ANALYST,
        responsibility=(
            "Ищет причины изменений продаж, тренды, конкурентные сигналы и гипотезы роста."
        ),
        input_data=["sales history", "competitors", "category trends", "marketplace analytics"],
        output_result=["аналитический отчет", "гипотезы", "объяснение отклонений"],
        included_agents=["AnalyticsAgent", "CompetitorAgent", "CategoryAgent"],
        telegram_commands=["/daily", "/agents", "/alerts"],
        no_approval_actions=["собрать отчет", "найти аномалии", "сформировать гипотезу"],
        approval_required_actions=["утвердить стратегическую гипотезу", "запустить эксперимент"],
    )

    def __init__(self) -> None:
        super().__init__([AnalyticsAgent(), CompetitorAgent(), CategoryAgent()])

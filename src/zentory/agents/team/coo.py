from zentory.agents.ads_agent import AdsAgent
from zentory.agents.analytics_agent import AnalyticsAgent
from zentory.agents.inventory_agent import InventoryAgent
from zentory.agents.team.base import BaseTeamRole
from zentory.schemas.team import TeamRoleDefinition, TeamRoleName


class AICOO(BaseTeamRole):
    definition = TeamRoleDefinition(
        role=TeamRoleName.COO,
        responsibility=(
            "Контролирует операционную надежность, SLA, approval queue, alerts и safe mode."
        ),
        input_data=["audit log", "action registry", "alerts", "agent statuses", "retry queue"],
        output_result=["операционный статус", "очередь approvals", "risk dashboard"],
        included_agents=["AnalyticsAgent", "AdsAgent", "InventoryAgent"],
        telegram_commands=["/status", "/alerts", "/agents", "/agent_status"],
        no_approval_actions=["показать статус", "собрать alerts", "проверить агентов"],
        approval_required_actions=[
            "разрешить controlled auto",
            "закрыть critical incident",
            "обойти safe mode",
        ],
    )

    def __init__(self) -> None:
        super().__init__([AnalyticsAgent(), AdsAgent(), InventoryAgent()])

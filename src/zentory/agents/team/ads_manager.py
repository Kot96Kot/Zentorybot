from zentory.agents.ads_agent import AdsAgent
from zentory.agents.team.base import BaseTeamRole
from zentory.schemas.team import TeamRoleDefinition, TeamRoleName


class AIAdsManager(BaseTeamRole):
    definition = TeamRoleDefinition(
        role=TeamRoleName.ADS_MANAGER,
        responsibility="Контролирует внутреннюю рекламу, ДРР, CTR, ставки и рекламные алерты.",
        input_data=["ads metrics", "sku margin", "stock days", "sales plan"],
        output_result=[
            "рекомендации по ставкам",
            "critical alerts",
            "список кампаний для проверки",
        ],
        included_agents=["AdsAgent"],
        telegram_commands=["/ads_today", "/alerts"],
        no_approval_actions=["собрать отчет", "подсветить высокий ДРР", "создать alert"],
        approval_required_actions=[
            "изменить ставку",
            "поставить кампанию на паузу",
            "увеличить бюджет",
        ],
    )

    def __init__(self) -> None:
        super().__init__([AdsAgent()])

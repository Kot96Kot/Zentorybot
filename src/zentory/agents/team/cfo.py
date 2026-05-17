from zentory.agents.promo_agent import PromoAgent
from zentory.agents.team.base import BaseTeamRole
from zentory.agents.unit_economics_agent import UnitEconomicsAgent
from zentory.schemas.team import TeamRoleDefinition, TeamRoleName


class AICFO(BaseTeamRole):
    definition = TeamRoleDefinition(
        role=TeamRoleName.CFO,
        responsibility="Защищает прибыль, маржинальность, цены, акции и финансовые ограничения.",
        input_data=["unit economics", "promo terms", "ad spend", "commission", "cost price"],
        output_result=["price guard", "promo decision", "margin risk report"],
        included_agents=["UnitEconomicsAgent", "PromoAgent"],
        telegram_commands=["/unit", "/promo_check", "/promo_list"],
        no_approval_actions=["рассчитать юнитку", "найти риск по марже", "собрать dangerous SKU"],
        approval_required_actions=[
            "изменить цену",
            "участвовать в акции",
            "согласовать минимальную маржу",
        ],
    )

    def __init__(self) -> None:
        super().__init__([UnitEconomicsAgent(), PromoAgent()])

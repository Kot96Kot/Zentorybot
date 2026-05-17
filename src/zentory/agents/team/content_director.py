from zentory.agents.content_agent import ContentAgent
from zentory.agents.feedback_agent import FeedbackAgent
from zentory.agents.team.base import BaseTeamRole
from zentory.schemas.team import TeamRoleDefinition, TeamRoleName


class AIContentDirector(BaseTeamRole):
    definition = TeamRoleDefinition(
        role=TeamRoleName.CONTENT_DIRECTOR,
        responsibility=(
            "Создает draft-контент карточек и управляет качеством первого экрана, SEO и отзывами."
        ),
        input_data=["content brief", "reviews", "questions", "CTR", "competitor content"],
        output_result=["draft карточки", "ТЗ на фото/инфографику", "задачи по отзывам"],
        included_agents=["ContentAgent", "FeedbackAgent"],
        telegram_commands=["/content_new", "/alerts"],
        no_approval_actions=["создать draft", "подготовить ТЗ", "сформировать черновик ответа"],
        approval_required_actions=[
            "опубликовать контент",
            "отправить ответ покупателю",
            "изменить карточку",
        ],
    )

    def __init__(self) -> None:
        super().__init__([ContentAgent(), FeedbackAgent()])

from typing import Any

from zentory.agents.base import BaseAgent
from zentory.core.enums import ApprovalMode
from zentory.decision.engine import DecisionEngine
from zentory.schemas.team import TeamRoleDefinition, TeamRoleResult


class BaseTeamRole:
    definition: TeamRoleDefinition

    def __init__(
        self, agents: list[BaseAgent], decision_engine: DecisionEngine | None = None
    ) -> None:
        self.agents = agents
        self.decision_engine = decision_engine or DecisionEngine()

    async def coordinate(self, event: dict[str, Any] | None = None) -> TeamRoleResult:
        event = event or {"event_type": "team_role_review", "payload": {"mock": True}}
        agent_results: list[dict[str, Any]] = []
        recommendations: list[str] = []
        actions_count = 0
        requires_human_approval = False

        for agent in self.agents:
            analysis = await agent.analyze(event)
            actions = await agent.propose_actions(event)
            decision = self.decision_engine.decide(event, actions)
            agent_results.append(
                {
                    "agent": agent.name,
                    "analysis": analysis,
                    "actions": [
                        action.model_dump(mode="json") for action in decision.proposed_actions
                    ],
                    "risk_level": decision.risk_level,
                    "approval_mode": decision.approval_mode,
                    "mock": True,
                }
            )
            actions_count += len(decision.proposed_actions)
            requires_human_approval = requires_human_approval or any(
                action.approval_mode != ApprovalMode.NONE for action in decision.proposed_actions
            )
            recommendations.extend(action.title for action in decision.proposed_actions[:3])

        if not recommendations:
            recommendations = ["Нет активных рекомендаций: продолжать мониторинг."]

        return TeamRoleResult(
            role=self.definition.role,
            summary=(
                f"{self.definition.role}: объединены агенты "
                f"{', '.join(self.definition.included_agents)}."
            ),
            agent_results=agent_results,
            recommendations=recommendations,
            actions_count=actions_count,
            requires_human_approval=requires_human_approval,
            next_telegram_commands=self.definition.telegram_commands,
            mock=True,
        )

    def describe(self) -> TeamRoleDefinition:
        return self.definition

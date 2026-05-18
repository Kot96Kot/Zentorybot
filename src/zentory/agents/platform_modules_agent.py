from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.services.platform_modules_service import PlatformModulesService


class PlatformModulesAgent(BaseAgent):
    name = "platform_modules"
    description = (
        "Forecast ABC, supply localization, content CTR, finance, "
        "learning loop and contracts"
    )
    supported_events = (
        "platform_modules",
        "forecast_abc",
        "supply_localization",
        "content_ctr",
        "finance_checker",
        "learning_loop",
        "data_contracts",
    )

    def __init__(self, service: PlatformModulesService | None = None) -> None:
        self.service = service or PlatformModulesService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        snapshot = self.service.build_snapshot()
        return {
            "agent": self.name,
            "event_type": str(event.get("event_type", "platform_modules")),
            "summary": snapshot.to_manager_summary(),
            "modules": snapshot.model_dump(mode="json"),
            "mock": True,
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        snapshot = self.service.build_snapshot()
        summary = snapshot.to_manager_summary()
        return [
            Action(
                agent_name=self.name,
                action_type="platform_modules_snapshot",
                title="Platform modules snapshot готов",
                description=(
                    "Mock-срез Forecast ABC, Supply Localization, Content CTR, "
                    "Finance Checker, Learning Loop и Data Contracts."
                ),
                payload={
                    "mock": True,
                    "source_event": event,
                    "summary": summary,
                    "modules": snapshot.model_dump(mode="json"),
                },
                risk_level=RiskLevel.MEDIUM,
                approval_mode=ApprovalMode.SOFT_APPROVAL,
                rollback_available=False,
                explanation=(
                    "Рекомендации не вызывают реальные API и требуют approval "
                    "для действий."
                ),
                evidence=[
                    {"source": "forecast_abc", "items": summary["forecast_items"]},
                    {"source": "supply_localization", "moves": summary["supply_moves"]},
                    {"source": "data_contracts", "contracts": summary["contracts"]},
                ],
            )
        ]

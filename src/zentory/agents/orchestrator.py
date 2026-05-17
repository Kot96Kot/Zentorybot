from typing import Any

from zentory.actions.registry import ActionRegistry
from zentory.actions.schemas import Action
from zentory.agents import (
    AdsAgent,
    AnalyticsAgent,
    CategoryAgent,
    CompetitorAgent,
    ContentAgent,
    FeedbackAgent,
    ForecastABCAgent,
    InventoryAgent,
    LaunchAgent,
    PromoAgent,
    SalesPlanAgent,
    SKUAgent,
    UnitEconomicsAgent,
)
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel
from zentory.decision.engine import DecisionEngine, DecisionResult
from zentory.services.audit_service import AuditService


class Orchestrator:
    CONTROL_EVENTS = {"control_start", "control_help", "control_status"}
    TELEGRAM_UX_EVENTS = {"daily", "alerts", "plan"}
    EVENT_ALIASES = {
        "daily": "analytics",
        "alerts": "ads_alerts",
        "plan": "sales_plan",
        "sku_overview": "sku_overview",
        "abc_revenue": "abc",
        "abc_profit": "abc",
    }

    def __init__(
        self,
        agents: list[BaseAgent] | None = None,
        decision_engine: DecisionEngine | None = None,
        action_registry: ActionRegistry | None = None,
        audit_service: AuditService | None = None,
    ) -> None:
        self.agents = agents or [
            SalesPlanAgent(),
            CompetitorAgent(),
            UnitEconomicsAgent(),
            ContentAgent(),
            AdsAgent(),
            PromoAgent(),
            InventoryAgent(),
            LaunchAgent(),
            FeedbackAgent(),
            ForecastABCAgent(),
            AnalyticsAgent(),
            CategoryAgent(),
            SKUAgent(),
        ]
        self.decision_engine = decision_engine or DecisionEngine()
        self.action_registry = action_registry or ActionRegistry()
        self.audit_service = audit_service or AuditService()

    async def handle_event(self, event: dict[str, Any]) -> DecisionResult:
        event_type = str(event.get("event_type", "unknown"))
        proposed_actions = []
        if event_type in self.CONTROL_EVENTS:
            proposed_actions = self._control_actions(event_type, event)
        elif event_type in self.TELEGRAM_UX_EVENTS:
            proposed_actions = self._telegram_ux_actions(event_type, event)
        agent_event_type = self.EVENT_ALIASES.get(event_type, event_type)
        agent_event = {**event, "event_type": agent_event_type}

        if not proposed_actions:
            for agent in self.agents:
                if agent.can_handle(agent_event_type):
                    proposed_actions.extend(await agent.propose_actions(agent_event))

        decision = self.decision_engine.decide(event, proposed_actions)
        await self.audit_service.record(
            {
                "event_type": "orchestrator_decision",
                "source_event_type": event_type,
                "resolved_event_type": agent_event_type,
                "risk_level": decision.risk_level,
                "approval_mode": decision.approval_mode,
                "proposed_actions_count": len(decision.proposed_actions),
                "mock": True,
            }
        )
        for action in decision.proposed_actions:
            self.action_registry.register(action)
        return decision

    def list_agents(self) -> list[dict[str, Any]]:
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "supported_events": list(agent.supported_events),
                "status": "mock_ready",
            }
            for agent in self.agents
        ]

    def _control_actions(self, event_type: str, event: dict[str, Any]) -> list[Action]:
        cards = {
            "control_start": {
                "status": "Zentorybot запущен",
                "problem": "агента выбирать не нужно",
                "reason": "Orchestrator сам маршрутизирует бизнес-команды",
                "recommendation": "начните с /daily, /alerts, /sku <sku> или /plan",
                "risk": "LOW",
            },
            "control_help": {
                "status": "доступны 10 команд",
                "problem": "старые команды отдельных агентов скрыты",
                "reason": "интерфейс должен быть управленческим, а не техническим",
                "recommendation": (
                    "/start /help /daily /alerts /sku <sku> /plan "
                    "/approve <id> /reject <id> /rollback <id> /status"
                ),
                "risk": "LOW",
            },
            "control_status": {
                "status": "все mock-агенты готовы; Safety Core активен",
                "problem": "реальные API отключены",
                "reason": "safe-mode защищает от изменения цен, ставок и карточек",
                "recommendation": "смотрите /alerts и подтверждайте действия через /approve",
                "risk": "LOW",
            },
        }
        return [
            self._telegram_action(
                event_type, cards[event_type], event, title=cards[event_type]["status"]
            )
        ]

    def _telegram_ux_actions(self, event_type: str, event: dict[str, Any]) -> list[Action]:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        sku = str(payload.get("sku", "WB-MOCK-1"))
        cards = {
            "daily": {
                "status": "отчет за вчера готов",
                "problem": "выручка -8%, реклама ACOS +4 п.п., остаток SKU WB-MOCK-1 на 5 дней",
                "reason": "просели заказы после роста ставки и снижения органики",
                "recommendation": "снизить ставку по убыточной кампании и пополнить WB-MOCK-1",
                "risk": "MEDIUM",
                "buttons": [
                    {"text": "План", "command": "/plan"},
                    {"text": "SKU", "command": "/sku WB-MOCK-1"},
                ],
            },
            "alerts": {
                "status": "найдено 2 срочных сигнала",
                "problem": "WB-MOCK-1 закончится через 5 дней; кампания ADS-7 выше ACOS-лимита",
                "reason": "остатки ниже safety-порога, рекламная ставка выросла быстрее продаж",
                "recommendation": "не усиливать рекламу до пополнения; проверить bid action",
                "risk": "HIGH",
                "buttons": [
                    {"text": "SKU", "command": "/sku WB-MOCK-1"},
                    {"text": "План", "command": "/plan"},
                ],
            },
            "sku_overview": {
                "status": f"SKU {sku}: карточка собрана",
                "problem": "остатка на 5 дней, CTR 1.8%, рейтинг 4.4, продажи -6%",
                "reason": "низкий запас ограничивает рекламу; отзывы про размер снижают конверсию",
                "recommendation": (
                    "пополнить склад, не повышать ставки, обновить блок размеров в карточке"
                ),
                "risk": "HIGH",
                "buttons": [
                    {"text": "План", "command": "/plan"},
                    {"text": "Alerts", "command": "/alerts"},
                ],
            },
            "plan": {
                "status": "план на сегодня готов",
                "problem": "3 задачи требуют управленческого решения",
                "reason": "приоритеты рассчитаны по риску денег, остатков и рекламы",
                "recommendation": (
                    "1) пополнить WB-MOCK-1; 2) снизить ADS-7; 3) обновить SKU-контент"
                ),
                "risk": "MEDIUM",
                "buttons": [
                    {"text": "Alerts", "command": "/alerts"},
                    {"text": "Status", "command": "/status"},
                ],
            },
        }
        return [
            self._telegram_action(
                event_type, cards[event_type], event, title=cards[event_type]["status"]
            )
        ]

    @staticmethod
    def _telegram_action(
        event_type: str, card: dict[str, Any], event: dict[str, Any], *, title: str
    ) -> Action:
        return Action(
            action_type=event_type,
            title=title,
            description=(
                "Mock Telegram UX response. Orchestrator selected the module automatically."
            ),
            payload={"mock": True, "source_event": event, "telegram_response": card},
            risk_level=RiskLevel.LOW,
        )

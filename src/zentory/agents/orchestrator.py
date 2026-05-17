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
    TELEGRAM_UX_EVENTS = {"daily", "alerts", "sku_overview", "plan"}
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
                "status": "SHADOW/ASSISTANT; Safety Core активен",
                "problem": "реальные API отключены; pending actions: mock 0",
                "reason": "mock mode включен, агенты готовы, safe-mode защищает от write-действий",
                "recommendation": "смотрите /alerts и подтверждайте действия через /approve",
                "risk": "LOW",
                "approval_required": "нет",
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
                "status": "сводка дня готова",
                "problem": (
                    "продажи -8%; остатки WB-MOCK-1 на 5 дней; реклама ACOS +4 п.п.; "
                    "отзывы: рейтинг 4.4; алерты: 2; рекомендации: 3"
                ),
                "reason": (
                    "просели заказы после роста ставки, снижения органики "
                    "и ограничения складского остатка"
                ),
                "recommendation": (
                    "проверить продажи, остатки, рекламу и отзывы; перейти в /alerts или /plan"
                ),
                "risk": "MEDIUM",
                "approval_required": "нет; есть pending approvals в /alerts",
                "buttons": [
                    {"text": "План", "command": "/plan"},
                    {"text": "SKU", "command": "/sku WB-MOCK-1"},
                ],
            },
            "alerts": {
                "status": "найдены critical/warning сигналы",
                "problem": (
                    "critical: WB-MOCK-1 закончится через 5 дней; warning: ADS-7 выше ACOS-лимита; "
                    "pending approvals: 1"
                ),
                "reason": "остатки ниже safety-порога, рекламная ставка выросла быстрее продаж",
                "recommendation": (
                    "не усиливать рекламу до пополнения; "
                    "подтвердить или отклонить pending action"
                ),
                "risk": "HIGH",
                "approval_required": "да, для pending action",
                "buttons": [
                    {"text": "SKU", "command": "/sku WB-MOCK-1"},
                    {"text": "План", "command": "/plan"},
                ],
            },
            "sku_overview": {
                "status": f"SKU {sku}: единая карточка собрана",
                "problem": (
                    "продажи -6%; остатки на 5 дней; реклама CTR 1.8%; отзывы рейтинг 4.4; "
                    "конкуренты дешевле на 7%; прогноз: риск stockout"
                ),
                "reason": (
                    "низкий запас ограничивает продажи и рекламу; "
                    "отзывы про размер снижают конверсию"
                ),
                "recommendation": (
                    "пополнить склад, не повышать ставки до поставки, "
                    "обновить блок размеров в карточке"
                ),
                "risk": "HIGH",
                "approval_required": "да, если создавать действие на пополнение или контент",
                "buttons": [
                    {"text": "План", "command": "/plan"},
                    {"text": "Alerts", "command": "/alerts"},
                ],
            },
            "plan": {
                "status": "план действий на день готов",
                "problem": (
                    "горит stockout WB-MOCK-1; нужно подтвердить ADS-7; "
                    "отложить низкий promo"
                ),
                "reason": (
                    "приоритеты рассчитаны по риску денег, остатков, "
                    "рекламы и pending approvals"
                ),
                "recommendation": (
                    "проверить остатки; подтвердить безопасные действия; "
                    "отложить низкомаржинальную акцию; "
                    "срочно разобрать critical alerts"
                ),
                "risk": "MEDIUM",
                "approval_required": "да, для действий из плана",
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
        risk_level = RiskLevel(card.get("risk", RiskLevel.LOW))
        return Action(
            action_type=event_type,
            title=title,
            description=(
                "Mock Telegram UX response. Orchestrator selected the module automatically."
            ),
            payload={"mock": True, "source_event": event, "telegram_response": card},
            risk_level=risk_level,
        )

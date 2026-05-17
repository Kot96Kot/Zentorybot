from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.schemas.finance import FinanceStatus
from zentory.services.finance_checker_service import FinanceCheckerService


class FinanceCheckerAgent(BaseAgent):
    name = "finance_checker"
    description = "Finance Checker: сверка PnL, DDS и unit profit по SKU"
    supported_events = ("finance_check", "pnl_check", "unit")

    def __init__(self, service: FinanceCheckerService | None = None) -> None:
        self.service = service or FinanceCheckerService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        event_type = str(event.get("event_type", "finance_check"))
        if event_type == "unit":
            sku = self._sku_from_event(event)
            unit = self.service.unit(sku)
            return {
                "agent": self.name,
                "mock": True,
                "unit": unit.model_dump(mode="json") if unit else None,
            }
        if event_type == "pnl_check":
            return {
                "agent": self.name,
                "mock": True,
                "pnl": self.service.pnl().model_dump(mode="json"),
            }
        return {
            "agent": self.name,
            "mock": True,
            "finance_check": self.service.check().model_dump(mode="json"),
        }

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        event_type = str(event.get("event_type", "finance_check"))
        if event_type == "unit":
            sku = self._sku_from_event(event)
            unit = self.service.unit(sku)
            if unit is None:
                card = {
                    "status": f"unit {sku} не найден",
                    "problem": "SKU отсутствует в mock finance dataset",
                    "reason": "FinanceChecker использует mock rows",
                    "recommendation": "проверьте SKU или загрузите финданные",
                    "risk": "MEDIUM",
                }
            else:
                card = {
                    "status": f"unit {sku}: {unit.status}",
                    "problem": f"profit={unit.profit}, margin={unit.margin_percent}",
                    "reason": "прибыль рассчитана по полной формуле расходов SKU",
                    "recommendation": "проверить issues перед изменением цены/рекламы",
                    "risk": "HIGH" if unit.status == FinanceStatus.CRITICAL else "LOW",
                    "unit": unit.model_dump(mode="json"),
                }
            return [self._action("unit", f"Unit finance check: {sku}", event, card)]
        if event_type == "pnl_check":
            pnl = self.service.pnl()
            card = {
                "status": f"PnL check: {pnl.status}",
                "problem": f"profit={pnl.total_profit}, margin={pnl.margin_percent}",
                "reason": "агрегированы mock unit economics по SKU",
                "recommendation": "сверить warning/critical SKU до финального отчета",
                "risk": "HIGH" if pnl.status == FinanceStatus.CRITICAL else "LOW",
                "pnl": pnl.model_dump(mode="json"),
            }
            return [self._action("pnl_check", "PnL finance check", event, card)]
        report = self.service.check()
        card = {
            "status": f"Finance check: {report.status}",
            "problem": f"issues={len(report.issues)}",
            "reason": "проверены PnL, DDS, unit profit и расхождения с внутренней таблицей",
            "recommendation": report.recommendation,
            "risk": "HIGH" if report.status == FinanceStatus.CRITICAL else "MEDIUM",
            "issues": [issue.model_dump(mode="json") for issue in report.issues[:10]],
        }
        return [self._action("finance_check", "Finance Checker report", event, card)]

    @staticmethod
    def _action(
        action_type: str, title: str, event: dict[str, Any], card: dict[str, Any]
    ) -> Action:
        risk = card.get("risk", "LOW")
        risk_level = (
            RiskLevel.HIGH
            if risk == "HIGH"
            else RiskLevel.MEDIUM
            if risk == "MEDIUM"
            else RiskLevel.LOW
        )
        return Action(
            agent_name="finance_checker",
            action_type=action_type,
            title=title,
            description="Mock-only finance check. Платежи и финальные отчеты не изменяются.",
            payload={"mock": True, "source_event": event, "telegram_response": card},
            risk_level=risk_level,
            approval_mode=ApprovalMode.NONE,
            rollback_available=False,
        )

    @staticmethod
    def _sku_from_event(event: dict[str, Any]) -> str:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        return str(payload.get("sku", "ZNT-PROFIT-001"))

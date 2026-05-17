from typing import Any

from zentory.actions.schemas import Action
from zentory.agents.base import BaseAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.abc import ABCClass, ABCMetric
from zentory.services.forecast_service import ForecastService


class ForecastABCAgent(BaseAgent):
    name = "forecast_abc"
    description = "Forecast & ABC анализ продаж и остатков"
    supported_events = ("abc", "forecast", "forecast_sku", "stock_forecast", "seasonality")

    def __init__(self, forecast_service: ForecastService | None = None) -> None:
        self.forecast_service = forecast_service or ForecastService()

    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        event_type = str(event.get("event_type", "abc"))
        if event_type == "seasonality":
            report = self.forecast_service.full_report()
            return {
                "agent": self.name,
                "mock": True,
                "seasonality": [item.model_dump(mode="json") for item in report.seasonality],
                "self_check": report.self_check.model_dump(mode="json"),
            }
        if event_type in {"forecast", "stock_forecast"}:
            report = self.forecast_service.stock_forecast_report()
            return {
                "agent": self.name,
                "mock": True,
                "stock_forecast": report.model_dump(mode="json"),
            }
        metric = self._metric_from_event(event)
        report = self.forecast_service.full_report(metric=metric)
        return {"agent": self.name, "mock": True, "forecast_abc": report.model_dump(mode="json")}

    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        event_type = str(event.get("event_type", "abc"))
        if event_type == "forecast_sku":
            return [self._sku_forecast_action(event)]
        if event_type in {"forecast", "stock_forecast"}:
            report = self.forecast_service.stock_forecast_report()
            critical = [
                item for item in report.items if item.stock_status in {"critical", "out_of_stock"}
            ]
            card = {
                "status": "stock forecast готов",
                "problem": f"critical/out_of_stock SKU: {len(critical)}",
                "reason": "расчет сделан на mock продажах, остатках и сезонности",
                "recommendation": "проверьте дозаказ по SKU с low coverage",
                "risk": "MEDIUM" if critical else "LOW",
                "self_check": "passed" if report.self_check.passed else "requires_human_review",
            }
            return [
                self._action(
                    event_type,
                    "Прогноз остатков 30/60/90",
                    event,
                    card,
                    risk_level=RiskLevel.MEDIUM if critical else RiskLevel.LOW,
                )
            ]
        return [self._abc_action(event)]

    def _abc_action(self, event: dict[str, Any]) -> Action:
        metric = self._metric_from_event(event)
        report = self.forecast_service.abc_report(metric=metric)
        total_revenue = self.forecast_service.abc_report(metric=ABCMetric.REVENUE).total_metric
        summary_by_class = {summary.abc_class: summary for summary in report.class_summary}
        a_summary = summary_by_class.get(ABCClass.A)
        b_summary = summary_by_class.get(ABCClass.B)
        c_summary = summary_by_class.get(ABCClass.C)
        a_count = a_summary.sku_count if a_summary else 0
        b_count = b_summary.sku_count if b_summary else 0
        c_count = c_summary.sku_count if c_summary else 0
        a_share = a_summary.share_percent if a_summary else 0
        b_share = b_summary.share_percent if b_summary else 0
        c_share = c_summary.share_percent if c_summary else 0
        card = {
            "status": f"ABC-анализ по {metric.value} готов",
            "problem": f"SKU в анализе: {len(report.rows)}, выручка 30д: {total_revenue:.0f}",
            "reason": "SKU отсортированы по метрике, доли и cumulative share перепроверены",
            "recommendation": (
                f"A-группа: {a_count} SKU / {a_share:.1f}%; "
                f"B-группа: {b_count} SKU / {b_share:.1f}%; "
                f"C-группа: {c_count} SKU / {c_share:.1f}%; "
                "проверьте forecast и закупку по топ-10"
            ),
            "risk": "LOW" if not report.warnings else "MEDIUM",
            "top_10": [row.model_dump(mode="json") for row in report.rows[:10]],
            "class_summary": [summary.model_dump(mode="json") for summary in report.class_summary],
            "warnings": report.warnings,
        }
        return self._action(
            "abc",
            "ABC-анализ SKU",
            event,
            card,
            risk_level=RiskLevel.MEDIUM if report.warnings else RiskLevel.LOW,
        )

    def _sku_forecast_action(self, event: dict[str, Any]) -> Action:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        sku = str(payload.get("sku", "ZNT-COS-001"))
        forecast = self.forecast_service.sku_forecast(sku)
        if forecast is None:
            card = {
                "status": f"SKU {sku} не найден",
                "problem": "SKU отсутствует в mock mapping",
                "reason": "данные берутся из mock MarketplaceSalesProvider",
                "recommendation": "проверьте SKU или product mapping",
                "risk": "MEDIUM",
                "self_check": "requires_human_review",
            }
        else:
            card = {
                "status": f"Forecast SKU {sku} готов",
                "problem": f"остаток {forecast.total_stock}, статус {forecast.stock_status}",
                "reason": (
                    f"ADS={forecast.avg_daily_sales}, coverage={forecast.stock_coverage_days}, "
                    f"seasonality={forecast.seasonality_coefficient}, "
                    f"trend={forecast.trend_coefficient}"
                ),
                "recommendation": (
                    "дозаказ 30/60/90: "
                    f"{forecast.recommended_replenishment_qty_30}/"
                    f"{forecast.recommended_replenishment_qty_60}/"
                    f"{forecast.recommended_replenishment_qty_90}"
                ),
                "risk": "HIGH" if forecast.stock_status in {"critical", "out_of_stock"} else "LOW",
                "forecast": forecast.model_dump(mode="json"),
                "self_check": "passed",
            }
        risk_level = RiskLevel.MEDIUM if card.get("risk") in {"MEDIUM", "HIGH"} else RiskLevel.LOW
        return self._action(
            "forecast_sku", f"Forecast SKU {sku}", event, card, risk_level=risk_level
        )

    @staticmethod
    def _action(
        action_type: str,
        title: str,
        event: dict[str, Any],
        card: dict[str, Any],
        *,
        risk_level: RiskLevel = RiskLevel.LOW,
    ) -> Action:
        return Action(
            action_type=action_type,
            title=title,
            description="Mock-only Forecast & ABC analysis. Реальных API-вызовов нет.",
            payload={"mock": True, "source_event": event, "telegram_response": card},
            risk_level=risk_level,
        )

    @staticmethod
    def _metric_from_event(event: dict[str, Any]) -> ABCMetric:
        payload = event.get("payload", {}) if isinstance(event.get("payload", {}), dict) else {}
        raw_metric = payload.get("metric") or payload.get("text") or ABCMetric.REVENUE
        if isinstance(raw_metric, str) and raw_metric.startswith("/abc"):
            parts = raw_metric.split()
            raw_metric = parts[1] if len(parts) > 1 else ABCMetric.REVENUE
        try:
            return ABCMetric(str(raw_metric))
        except ValueError:
            return ABCMetric.REVENUE

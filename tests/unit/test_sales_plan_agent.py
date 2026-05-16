import pytest

from zentory.agents.sales_plan_agent import SalesPlanAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.sales_plan import SalesPlanStatus
from zentory.services.sales_plan_service import SalesPlanService


@pytest.mark.asyncio
async def test_sales_plan_agent_returns_reports_for_sales_plan_command() -> None:
    agent = SalesPlanAgent()

    analysis = await agent.analyze({"event_type": "sales_plan", "payload": {"mock": True}})

    assert analysis["mock"] is True
    assert analysis["reports"]
    assert analysis["reports"][0]["day_plan"] > 0
    assert analysis["reports"][0]["week_plan"] == analysis["reports"][0]["day_plan"] * 7
    assert analysis["reports"][0]["month_plan"] == analysis["reports"][0]["day_plan"] * 30


@pytest.mark.asyncio
async def test_sales_plan_agent_filters_by_sku_and_creates_alert_actions() -> None:
    agent = SalesPlanAgent()

    actions = await agent.propose_actions(
        {"event_type": "sales_plan_sku", "payload": {"sku": "ZNT-OZON-002"}}
    )

    assert actions
    assert all(action.payload["report"]["sku"] == "ZNT-OZON-002" for action in actions)
    assert any(action.action_type == "sales_plan_alert" for action in actions)
    assert any(action.risk_level == RiskLevel.MEDIUM for action in actions)


def test_sales_plan_service_marks_critical_when_fact_is_more_than_30_percent_below_plan() -> None:
    service = SalesPlanService()

    report = service.calculate_reports(sku="ZNT-YM-003")[0]

    assert report.status == SalesPlanStatus.CRITICAL
    assert report.tasks == ["Заказов нет, но показы есть: создать задачу на анализ карточки."]
    assert report.deviation_percent < -30

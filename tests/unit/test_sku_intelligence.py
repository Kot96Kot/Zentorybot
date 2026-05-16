import pytest

from zentory.agents.sku_agent import SKUAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.services.sku_intelligence_service import SKUIntelligenceService


def test_sku_intelligence_card_contains_management_picture() -> None:
    card = SKUIntelligenceService().build_card("WB-MOCK-1")

    assert card.sku == "WB-MOCK-1"
    assert card.articles.wildberries == "WB-ART-WB-MOCK-1"
    assert card.articles.ozon == "OZON-ART-WB-MOCK-1"
    assert card.articles.yandex_market == "YM-ART-WB-MOCK-1"
    assert card.name
    assert card.sales.day_units > 0
    assert card.sales.week_units >= card.sales.day_units
    assert card.sales.month_units >= card.sales.week_units
    assert card.sales.revenue > 0
    assert card.sales.margin_percent > 0
    assert card.stock.stock_units > 0
    assert card.stock.coverage_days == 5
    assert card.advertising.drr_percent > 0
    assert card.advertising.ctr_percent > 0
    assert card.advertising.clicks > 0
    assert card.advertising.carts > 0
    assert card.advertising.orders > 0
    assert card.advertising.cart_conversion_percent > 0
    assert card.advertising.order_conversion_percent > 0
    assert card.reviews.rating > 0
    assert card.reviews.reviews_count > 0
    assert card.search_position > 0
    assert card.competitor.sku
    assert card.strengths
    assert card.weaknesses
    assert card.recommendations
    assert card.risks
    assert card.approval_actions


def test_sku_intelligence_manager_card_is_short_and_actionable() -> None:
    service = SKUIntelligenceService()
    card = service.build_card("WB-MOCK-1")

    manager_card = service.to_manager_card(card)

    assert manager_card["status"] == "SKU WB-MOCK-1: intelligence card собрана"
    assert "реклама" in str(manager_card["problem"])
    assert "отзывы" in str(manager_card["problem"])
    assert "Пополнить склад" in str(manager_card["recommendation"])
    assert manager_card["risk"] == "HIGH"
    assert manager_card["buttons"]


@pytest.mark.asyncio
async def test_sku_agent_returns_action_with_card_payload() -> None:
    action = (await SKUAgent().propose_actions({"payload": {"sku": "OZON-MOCK-2"}}))[0]

    assert action.agent_name == "sku_intelligence"
    assert action.action_type == "sku_intelligence_card"
    assert action.risk_level == RiskLevel.HIGH
    assert action.approval_mode == ApprovalMode.HARD_APPROVAL
    assert action.payload["sku_intelligence"]["sku"] == "OZON-MOCK-2"
    assert action.payload["telegram_response"]["status"] == (
        "SKU OZON-MOCK-2: intelligence card собрана"
    )
    assert action.evidence

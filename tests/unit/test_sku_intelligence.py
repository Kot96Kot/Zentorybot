import asyncio

from zentory.agents.sku_agent import SKUAgent
from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.services.sku_intelligence_service import SKUIntelligenceService


def test_sku_intelligence_card_contains_required_management_blocks() -> None:
    card = SKUIntelligenceService().build_card("WB-MOCK-1")

    assert card.basic.sku == "WB-MOCK-1"
    assert card.basic.nm_id
    assert card.basic.vendor_code == "VENDOR-WB-MOCK-1"
    assert card.basic.marketplace == "wildberries"
    assert card.basic.product_name
    assert card.basic.category
    assert card.basic.brand

    assert card.sales.sales_qty_day > 0
    assert card.sales.sales_qty_7d >= card.sales.sales_qty_day
    assert card.sales.sales_qty_30d >= card.sales.sales_qty_7d
    assert card.sales.revenue_day > 0
    assert card.sales.revenue_30d > card.sales.revenue_day
    assert card.sales.avg_price > 0
    assert card.sales.buyout_percent > 0

    assert card.stock.total_stock == 92
    assert card.stock.stock_by_warehouse["Коледино"] > 0
    assert card.stock.days_of_coverage == 5
    assert card.stock.stock_status == "low_stock"

    assert card.advertising.impressions > 0
    assert card.advertising.ctr == 1.8
    assert card.advertising.clicks > 0
    assert card.advertising.spend > 0
    assert card.advertising.drr == 17.8
    assert card.advertising.orders_from_ads > 0
    assert card.advertising.campaign_status == "limited_by_stock"

    assert card.conversion.cart_conversion > 0
    assert card.conversion.order_conversion > 0
    assert card.conversion.click_to_order > 0

    assert card.reputation.rating == 4.4
    assert card.reputation.reviews_count > 0
    assert card.reputation.negative_reviews_count > 0
    assert card.reputation.unanswered_questions > 0

    assert card.competitor.competitor_sku == "COMP-MOCK-9"
    assert card.competitor.competitor_price > 0
    assert card.competitor.competitor_rating > card.reputation.rating
    assert card.competitor.where_we_are_stronger
    assert card.competitor.where_we_are_weaker

    assert card.risks.low_stock is True
    assert card.risks.high_drr is True
    assert card.risks.low_ctr is True
    assert card.risks.low_margin is False
    assert card.risks.rating_risk is True
    assert card.risks.out_of_stock is True

    assert card.recommendations
    assert all(recommendation.title for recommendation in card.recommendations)
    assert all(recommendation.reason for recommendation in card.recommendations)
    assert all(recommendation.expected_effect for recommendation in card.recommendations)
    assert any(recommendation.approval_required for recommendation in card.recommendations)


def test_sku_intelligence_manager_card_is_short_and_actionable() -> None:
    service = SKUIntelligenceService()
    card = service.build_card("WB-MOCK-1")

    manager_card = service.to_manager_card(card)

    assert manager_card["status"] == "SKU WB-MOCK-1: SKU Intelligence Card собрана"
    assert "продажи" in str(manager_card["problem"])
    assert "остаток" in str(manager_card["problem"])
    assert "реклама" in str(manager_card["problem"])
    assert "отзывы" in str(manager_card["problem"])
    assert "конкуренты" in str(manager_card["problem"])
    assert "прогноз" in str(manager_card["problem"])
    assert "Пополнить склад" in str(manager_card["recommendation"])
    assert manager_card["risk"] == "HIGH"
    assert manager_card["approval_required"] == "да"
    assert manager_card["buttons"]


def test_sku_agent_returns_action_with_card_payload() -> None:
    action = asyncio.run(SKUAgent().propose_actions({"payload": {"sku": "OZON-MOCK-2"}}))[0]

    assert action.agent_name == "sku_intelligence"
    assert action.action_type == "sku_intelligence_card"
    assert action.risk_level == RiskLevel.HIGH
    assert action.approval_mode == ApprovalMode.HARD_APPROVAL
    assert action.payload["sku_intelligence"]["basic"]["sku"] == "OZON-MOCK-2"
    assert action.payload["sku_intelligence"]["sales"]["sales_qty_7d"] == 116
    assert action.payload["sku_intelligence"]["risks"]["out_of_stock"] is True
    assert action.payload["telegram_response"]["status"] == (
        "SKU OZON-MOCK-2: SKU Intelligence Card собрана"
    )
    assert action.evidence

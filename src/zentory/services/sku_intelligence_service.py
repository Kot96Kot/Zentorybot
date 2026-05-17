from zentory.core.enums import RiskLevel
from zentory.schemas.sku_intelligence import (
    SKUAdvertisingMetrics,
    SKUBasicInfo,
    SKUCompetitorComparison,
    SKUConversionMetrics,
    SKUIntelligenceCard,
    SKURecommendation,
    SKUReputationMetrics,
    SKURiskFlags,
    SKUSalesMetrics,
    SKUStockMetrics,
)


class SKUIntelligenceService:
    def build_card(self, sku: str) -> SKUIntelligenceCard:
        normalized_sku = sku or "WB-MOCK-1"
        return SKUIntelligenceCard(
            basic=SKUBasicInfo(
                sku=normalized_sku,
                nm_id=1_234_567,
                vendor_code=f"VENDOR-{normalized_sku}",
                marketplace=self._marketplace_for(normalized_sku),
                product_name="Mock базовый товар Zentory",
                category="Дом и кухня",
                brand="Zentory Mock Brand",
            ),
            sales=SKUSalesMetrics(
                sales_qty_day=18,
                sales_qty_7d=116,
                sales_qty_30d=482,
                revenue_day=18_180.0,
                revenue_30d=486_240.0,
                avg_price=1_008.8,
                buyout_percent=92.5,
                margin_percent=24.5,
            ),
            stock=SKUStockMetrics(
                total_stock=92,
                stock_by_warehouse={
                    "Коледино": 41,
                    "Электросталь": 28,
                    "Казань": 23,
                },
                days_of_coverage=5,
                stock_status="low_stock",
            ),
            advertising=SKUAdvertisingMetrics(
                impressions=180_000,
                ctr=1.8,
                clicks=3_240,
                spend=86_550.0,
                drr=17.8,
                orders_from_ads=84,
                campaign_status="limited_by_stock",
                carts=226,
            ),
            conversion=SKUConversionMetrics(
                cart_conversion=7.0,
                order_conversion=2.6,
                click_to_order=2.6,
            ),
            reputation=SKUReputationMetrics(
                rating=4.4,
                reviews_count=138,
                negative_reviews_count=11,
                unanswered_questions=4,
                latest_reviews=[
                    "Покупатели хвалят качество ткани",
                    "Повторяется замечание: размер маломерит",
                ],
            ),
            competitor=SKUCompetitorComparison(
                competitor_sku="COMP-MOCK-9",
                competitor_price=970.0,
                competitor_rating=4.7,
                where_we_are_stronger=[
                    "Маржа выше минимального порога",
                    "Есть стабильные заказы за неделю",
                    "Качество товара позитивно отмечают в отзывах",
                ],
                where_we_are_weaker=[
                    "Остатка меньше 7 дней",
                    "CTR ниже целевого уровня 2.5%",
                    "Рейтинг и цена хуже основного конкурента",
                ],
            ),
            risks=SKURiskFlags(
                low_stock=True,
                high_drr=True,
                low_ctr=True,
                low_margin=False,
                rating_risk=True,
                out_of_stock=True,
            ),
            recommendations=[
                SKURecommendation(
                    title="Пополнить склад до усиления рекламы",
                    reason="Покрытие всего 5 дней, реклама уже ограничена остатками.",
                    expected_effect=(
                        "Снизит риск stockout и позволит безопасно масштабировать продажи."
                    ),
                    risk_level=RiskLevel.HIGH,
                    approval_required=True,
                ),
                SKURecommendation(
                    title="Не повышать ставки до поставки",
                    reason="ДРР 17.8% при низком CTR и малом покрытии.",
                    expected_effect="Сохранит маржу и не ускорит распродажу последнего остатка.",
                    risk_level=RiskLevel.MEDIUM,
                    approval_required=True,
                ),
                SKURecommendation(
                    title="Обновить размерную сетку и первый экран карточки",
                    reason="В отзывах повторяется возражение про размер, CTR ниже целевого уровня.",
                    expected_effect=(
                        "Повысит CTR и конверсию в корзину без write-действий в mock-режиме."
                    ),
                    risk_level=RiskLevel.LOW,
                    approval_required=False,
                ),
            ],
        )

    def to_manager_card(self, card: SKUIntelligenceCard) -> dict[str, object]:
        recommendations = "; ".join(item.title for item in card.recommendations)
        reasons = "; ".join(item.reason for item in card.recommendations)
        risk = "HIGH" if card.active_risks else "LOW"
        approval_required = any(item.approval_required for item in card.recommendations)
        return {
            "status": f"SKU {card.sku}: SKU Intelligence Card собрана",
            "problem": (
                f"продажи {card.sales.sales_qty_7d} шт/7д; "
                f"остаток {card.stock.total_stock} шт. на {card.stock.days_of_coverage} дней; "
                f"реклама: CTR {card.advertising.ctr}%, ДРР {card.advertising.drr}%; "
                f"отзывы: рейтинг {card.reputation.rating}, "
                f"негативных {card.reputation.negative_reviews_count}; "
                f"конкуренты: {card.competitor.competitor_sku} дешевле/сильнее по рейтингу; "
                "прогноз: есть риск stockout"
            ),
            "reason": reasons,
            "recommendation": recommendations,
            "risk": risk,
            "approval_required": "да" if approval_required else "нет",
            "buttons": [
                {"text": item.title, "command": f"/sku {card.sku}"}
                for item in card.recommendations
            ],
        }

    def list_top_risky_skus(self) -> list[dict[str, object]]:
        return [
            self.build_card("WB-MOCK-1").to_summary(),
            self.build_card("OZON-MOCK-2").to_summary(),
        ]

    @staticmethod
    def _marketplace_for(sku: str) -> str:
        if sku.upper().startswith("OZON") or "OZON" in sku.upper():
            return "ozon"
        if sku.upper().startswith("YM") or "YANDEX" in sku.upper():
            return "yandex_market"
        return "wildberries"

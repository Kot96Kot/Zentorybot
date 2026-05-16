from zentory.core.enums import ApprovalMode, RiskLevel
from zentory.schemas.sku_intelligence import (
    AdvertisingSnapshot,
    ApprovalAction,
    CompetitorSnapshot,
    MarketplaceArticles,
    ReviewSnapshot,
    SalesSnapshot,
    SKUIntelligenceCard,
    StockSnapshot,
)


class SKUIntelligenceService:
    def build_card(self, sku: str) -> SKUIntelligenceCard:
        normalized_sku = sku or "WB-MOCK-1"
        return SKUIntelligenceCard(
            sku=normalized_sku,
            articles=MarketplaceArticles(
                wildberries=f"WB-ART-{normalized_sku}",
                ozon=f"OZON-ART-{normalized_sku}",
                yandex_market=f"YM-ART-{normalized_sku}",
            ),
            name="Mock базовый товар Zentory",
            sales=SalesSnapshot(
                day_units=18,
                week_units=116,
                month_units=482,
                revenue=486_240.0,
                margin_percent=24.5,
            ),
            stock=StockSnapshot(stock_units=92, coverage_days=5),
            advertising=AdvertisingSnapshot(
                drr_percent=17.8,
                ctr_percent=1.8,
                clicks=3240,
                carts=226,
                orders=84,
                cart_conversion_percent=7.0,
                order_conversion_percent=2.6,
            ),
            reviews=ReviewSnapshot(
                rating=4.4,
                reviews_count=138,
                latest_reviews=[
                    "Покупатели хвалят качество ткани",
                    "Повторяется замечание: размер маломерит",
                ],
            ),
            search_position=18,
            competitor=CompetitorSnapshot(
                sku="COMP-MOCK-9",
                name="Конкурент с похожей ценой",
                price=970.0,
                rating=4.7,
                search_position=9,
            ),
            strengths=[
                "Маржа выше минимального порога",
                "Есть стабильные заказы за неделю",
                "Качество товара позитивно отмечают в отзывах",
            ],
            weaknesses=[
                "Остатка меньше 7 дней",
                "CTR ниже целевого уровня 2.5%",
                "Позиция в поиске хуже основного конкурента",
            ],
            recommendations=[
                "Пополнить склад до усиления рекламы",
                "Не повышать ставки, пока покрытие меньше 7 дней",
                "Обновить размерную сетку и первый экран карточки",
            ],
            risks=[
                "Out-of-stock в течение недели",
                "Рост ДРР без роста заказов",
                "Потеря поисковой позиции конкуренту COMP-MOCK-9",
            ],
            approval_actions=[
                ApprovalAction(
                    action_id=f"{normalized_sku}-content-fix",
                    title="Обновить блок размеров в карточке",
                    risk_level=RiskLevel.LOW,
                    approval_mode=ApprovalMode.NONE,
                    rollback_available=True,
                    command=f"/approve {normalized_sku}-content-fix",
                ),
                ApprovalAction(
                    action_id=f"{normalized_sku}-ads-hold",
                    title="Приостановить повышение ставок до пополнения",
                    risk_level=RiskLevel.MEDIUM,
                    approval_mode=ApprovalMode.SOFT_APPROVAL,
                    rollback_available=True,
                    command=f"/approve {normalized_sku}-ads-hold",
                ),
            ],
        )

    def to_manager_card(self, card: SKUIntelligenceCard) -> dict[str, object]:
        return {
            "status": f"SKU {card.sku}: intelligence card собрана",
            "problem": (
                f"остаток {card.stock.stock_units} шт. на {card.stock.coverage_days} дней; "
                f"реклама: ДРР {card.advertising.drr_percent}%; "
                f"отзывы: рейтинг {card.reviews.rating}; позиция #{card.search_position}"
            ),
            "reason": "; ".join(card.weaknesses),
            "recommendation": "; ".join(card.recommendations),
            "risk": "HIGH" if card.risks else "LOW",
            "buttons": [
                {"text": action.title, "command": action.command}
                for action in card.approval_actions
            ],
        }

    def list_top_risky_skus(self) -> list[dict[str, object]]:
        return [
            self.build_card("WB-MOCK-1").to_summary(),
            self.build_card("OZON-MOCK-2").to_summary(),
        ]

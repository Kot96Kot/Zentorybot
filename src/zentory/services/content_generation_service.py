from abc import ABC, abstractmethod
from typing import Any

from zentory.schemas.content import (
    ContentBrief,
    ContentCardDraft,
    InfographicTask,
    PhotoTask,
    VideoTask,
)


class ContentLLMProvider(ABC):
    name: str

    @abstractmethod
    async def generate_card(self, brief: ContentBrief) -> ContentCardDraft:
        """Generate a draft content card from a minimal marketplace brief."""


class MockContentLLMProvider(ContentLLMProvider):
    name = "mock"

    async def generate_card(self, brief: ContentBrief) -> ContentCardDraft:
        pain = brief.customer_pains[0] if brief.customer_pains else "экономия времени"
        key_characteristics = ", ".join(
            f"{key}: {value}" for key, value in brief.main_characteristics.items()
        )
        competitor_context = ", ".join(brief.competitors) or "категорийные конкуренты"
        seo_title = self._seo_title(brief)
        keywords = self._keywords(brief)
        return ContentCardDraft(
            marketplace=brief.marketplace,
            sku=brief.sku,
            article=brief.article,
            seo_title=seo_title,
            description=(
                f"{brief.product_name} {brief.brand} — mock-черновик карточки для категории "
                f"«{brief.category}». Товар помогает закрыть боль покупателя: {pain}. "
                f"Ключевые характеристики: {key_characteristics or 'уточняются в брифе'}. "
                f"Позиционирование учитывает конкурентов: {competitor_context}."
            ),
            unique_selling_propositions=[
                f"Решает задачу покупателя: {pain}.",
                "Структура карточки подготовлена под SEO и конверсию.",
                "Черновик не публикуется без approval менеджера.",
            ],
            benefits=[
                "Понятное первое фото с главным сценарием использования.",
                "Характеристики вынесены в инфографику без перегруза текста.",
                "Описание отвечает на основные сомнения покупателя.",
            ],
            characteristics=brief.main_characteristics,
            infographic_tasks=[
                InfographicTask(
                    slide=1,
                    title="Главное УТП",
                    message=f"Показать, как товар решает боль: {pain}.",
                    visual_direction="Крупный товар, короткий benefit headline, 2-3 иконки.",
                ),
                InfographicTask(
                    slide=2,
                    title="Характеристики",
                    message=key_characteristics or "Собрать ключевые параметры из брифа.",
                    visual_direction="Сетка характеристик, чистый фон, акцент на цифрах.",
                ),
                InfographicTask(
                    slide=3,
                    title="Сравнение",
                    message=f"Показать отличие от: {competitor_context}.",
                    visual_direction="Таблица сравнения без упоминания запрещенных утверждений.",
                ),
            ],
            photo_tasks=[
                PhotoTask(
                    shot=1,
                    title="Главное фото",
                    requirements="Товар крупно, белый/светлый фон, без лишних надписей.",
                ),
                PhotoTask(
                    shot=2,
                    title="Товар в сценарии",
                    requirements="Показать использование в реальной ситуации покупателя.",
                ),
                PhotoTask(
                    shot=3,
                    title="Комплектация и детали",
                    requirements=(
                        "Разложить комплект, показать фактуру, кнопки, размеры или состав."
                    ),
                ),
            ],
            video_tasks=[
                VideoTask(
                    scene=1,
                    title="Проблема",
                    script=f"Показать боль покупателя: {pain}.",
                ),
                VideoTask(
                    scene=2,
                    title="Решение",
                    script=f"Продемонстрировать {brief.product_name} в действии.",
                ),
                VideoTask(
                    scene=3,
                    title="Доказательство",
                    script="Показать результат, комплектацию и финальный call-to-action.",
                ),
            ],
            keywords=keywords,
            pre_publish_checklist=[
                "Проверить соответствие ограничениям площадки.",
                "Проверить, что нет медицинских/запрещенных обещаний без доказательств.",
                "Проверить SEO-название на длину и читаемость.",
                "Согласовать draft с менеджером перед публикацией.",
                "Убедиться, что фото и инфографика соответствуют требованиям marketplace.",
            ],
            llm_provider=self.name,
            mock=True,
        )

    @staticmethod
    def _seo_title(brief: ContentBrief) -> str:
        core = f"{brief.product_name} {brief.brand}"
        category = brief.category.lower()
        return f"{core} для {category}, арт. {brief.article}"

    @staticmethod
    def _keywords(brief: ContentBrief) -> list[str]:
        words = [brief.product_name, brief.category, brief.brand, brief.article]
        words.extend(brief.customer_pains)
        words.extend(str(value) for value in brief.main_characteristics.values())
        return [word.lower() for word in words if word]


class ContentGenerationService:
    def __init__(self, provider: ContentLLMProvider | None = None) -> None:
        self.provider = provider or MockContentLLMProvider()

    async def generate_draft(self, brief: ContentBrief) -> ContentCardDraft:
        return await self.provider.generate_card(brief)

    def build_mock_brief(
        self, sku: str | None = None, payload: dict[str, Any] | None = None
    ) -> ContentBrief:
        payload = payload or {}
        if payload.get("product_name"):
            return ContentBrief(
                marketplace=str(payload.get("marketplace", "wildberries")),
                category=str(payload.get("category", "товары для дома")),
                product_name=str(payload["product_name"]),
                brand=str(payload.get("brand", "Zentory")),
                article=str(payload.get("article", sku or "MOCK-ARTICLE")),
                price=float(payload.get("price", 1990)),
                main_characteristics=dict(payload.get("main_characteristics", {})),
                customer_pains=list(payload.get("customer_pains", [])),
                competitors=list(payload.get("competitors", [])),
                marketplace_restrictions=list(payload.get("marketplace_restrictions", [])),
                sku=sku or payload.get("sku"),
            )
        return self._mock_vacuum_sealer_brief(sku)

    @staticmethod
    def _mock_vacuum_sealer_brief(sku: str | None = None) -> ContentBrief:
        return ContentBrief(
            marketplace="wildberries",
            category="кухонная техника",
            product_name="вакууматор для продуктов",
            brand="Zentory Home",
            article="VAC-FOOD-001",
            price=3490,
            main_characteristics={
                "мощность": "110 Вт",
                "режимы": "сухой и влажный продукт",
                "ширина пакета": "до 30 см",
                "материал": "ABS-пластик",
            },
            customer_pains=[
                "продукты быстро портятся",
                "мало места в морозилке",
                "сложно хранить заготовки без запахов",
            ],
            competitors=["Kitfort", "Redmond", "Xiaomi"],
            marketplace_restrictions=["не обещать увеличение срока хранения без условий"],
            sku=sku or "ZNT-CONTENT-001",
        )

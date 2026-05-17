from zentory.schemas.content_ctr import (
    ContentBriefCTR,
    ContentCTRFactoryResult,
    ContentPhotoHypothesis,
    ContentRisk,
    CTRTestPlan,
    GeneratedImagePrompts,
)
from zentory.services.content_reference_service import ContentReferenceService
from zentory.services.prompt_generation_service import PromptGenerationService


class ContentCTRService:
    def __init__(
        self,
        reference_service: ContentReferenceService | None = None,
        prompt_service: PromptGenerationService | None = None,
    ) -> None:
        self.reference_service = reference_service or ContentReferenceService()
        self.prompt_service = prompt_service or PromptGenerationService()

    def build_brief(self, payload: dict[str, object] | None = None) -> ContentBriefCTR:
        return self.reference_service.brief_from_payload(payload)

    def build_for_sku(self, sku: str) -> ContentCTRFactoryResult:
        brief = self.reference_service.build_mock_brief(sku)
        hypotheses = self.generate_hypotheses(brief)
        prompts = self.generate_prompts(brief, hypotheses[:3])
        return ContentCTRFactoryResult(
            brief=brief,
            hypotheses=hypotheses,
            prompts=prompts,
            ctr_test_plan=self.build_test_plan(brief),
            safety_notes=self.safety_notes(),
            mock_mode=True,
        )

    def generate_hypotheses(self, brief: ContentBriefCTR) -> list[ContentPhotoHypothesis]:
        pains = brief.buyer_pains or ["покупатель не видит пользу товара"]
        features = brief.key_features or ["ключевое преимущество товара"]
        templates = [
            (
                "Before/after на первом фото",
                "Контраст быстрее объясняет выгоду и может поднять CTR.",
                pains[0],
                "визуальный split-screen до/после",
                ContentRisk.MEDIUM,
            ),
            (
                "Крупный товар + 3 коротких benefit badges",
                "Покупатель считывает функции без перехода в описание.",
                pains[min(1, len(pains) - 1)],
                "количество и формулировки бейджей",
                ContentRisk.LOW,
            ),
            (
                "Lifestyle-сцена с реальным сценарием использования",
                "Сценарий помогает представить товар дома и снижает сомнения.",
                pains[min(2, len(pains) - 1)],
                "фон, реквизит и действие рук в кадре",
                ContentRisk.MEDIUM,
            ),
            (
                "Главное фото с измеримой выгодой",
                "Цифра на фото делает пользу конкретной и повышает заметность в выдаче.",
                pains[0],
                f"цифровой акцент на фиче: {features[0]}",
                ContentRisk.HIGH,
            ),
            (
                "Сравнение с типичной проблемой конкурентов",
                "Помогает отстроиться без прямого нарушения правил маркетплейса.",
                pains[0],
                "мягкое сравнение без чужих логотипов",
                ContentRisk.HIGH,
            ),
            (
                "Минималистичное premium-фото",
                "Чистый кадр может повысить доверие и воспринимаемую цену.",
                "сомнение в качестве товара",
                "уровень минимализма и тени",
                ContentRisk.LOW,
            ),
        ]
        return [
            ContentPhotoHypothesis(
                idea=idea,
                why_it_may_work=why,
                pain_addressed=pain,
                element_to_test=element,
                risk=risk,
                draft_only=True,
                mock_mode=True,
            )
            for idea, why, pain, element, risk in templates
        ]

    def generate_prompts(
        self,
        brief: ContentBriefCTR,
        hypotheses: list[ContentPhotoHypothesis] | None = None,
    ) -> list[GeneratedImagePrompts]:
        hypotheses = hypotheses or self.generate_hypotheses(brief)[:3]
        return self.prompt_service.generate_prompts(brief, hypotheses)

    def build_test_plan(self, brief: ContentBriefCTR) -> CTRTestPlan:
        return CTRTestPlan(
            what_we_test="Главное фото карточки: текущий вариант против draft-гипотезы",
            success_metric=f"CTR from {brief.current_ctr}% to target {brief.target_ctr}%",
            test_period="7 дней или до набора минимального трафика",
            minimum_traffic=2_000,
            winner_criteria="Победитель: CTR выше минимум на 15% без падения конверсии в заказ",
            publication_requires_approval=True,
            bulk_change_requires_hard_approval=True,
            mock_mode=True,
        )

    @staticmethod
    def safety_notes() -> list[str]:
        return [
            "Контент не публикуется автоматически.",
            "Все изменения карточки создаются только как draft.",
            "Публикация требует approval менеджера.",
            "Массовое изменение контента требует hard approval.",
            "Реальная генерация изображений не выполняется: только mock prompts.",
        ]

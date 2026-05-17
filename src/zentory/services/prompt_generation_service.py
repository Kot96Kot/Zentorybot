from zentory.schemas.content_ctr import (
    ContentBriefCTR,
    ContentPhotoHypothesis,
    GeneratedImagePrompts,
)


class PromptGenerationService:
    def generate_prompts(
        self, brief: ContentBriefCTR, hypotheses: list[ContentPhotoHypothesis]
    ) -> list[GeneratedImagePrompts]:
        return [self.prompt_for(brief, hypothesis) for hypothesis in hypotheses]

    def prompt_for(
        self, brief: ContentBriefCTR, hypothesis: ContentPhotoHypothesis
    ) -> GeneratedImagePrompts:
        base = (
            f"Marketplace hero image for {brief.product_name}, category {brief.category}. "
            f"Target audience: {brief.target_audience}. Hypothesis: {hypothesis.idea}. "
            f"Show the product clearly, high conversion ecommerce composition, clean lighting, "
            f"realistic materials, no fake logos, no automatic publication, draft concept only."
        )
        text_blocks = [
            f"Главная выгода: {hypothesis.pain_addressed}",
            f"Проверить: {hypothesis.element_to_test}",
        ]
        return GeneratedImagePrompts(
            sora_prompt=(
                base
                + " Create a short product-video style key frame with a simple before/after story."
            ),
            gpt_image_prompt=(
                base
                + " Generate one square 1:1 marketplace main image, "
                + "photorealistic, readable layout."
            ),
            midjourney_prompt=(
                base
                + " --ar 1:1 --style raw --v 6 --no watermark --no distorted text"
            ),
            russian_text_blocks=text_blocks,
            language="en",
            draft_only=True,
            mock_mode=True,
        )

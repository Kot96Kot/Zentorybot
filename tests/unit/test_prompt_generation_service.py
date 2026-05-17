from zentory.services.content_ctr_service import ContentCTRService
from zentory.services.prompt_generation_service import PromptGenerationService


def test_prompt_generation_creates_english_prompts_and_separate_russian_blocks() -> None:
    service = ContentCTRService()
    brief = service.build_brief({"sku": "SKU-PROMPT"})
    hypothesis = service.generate_hypotheses(brief)[0]

    prompt = PromptGenerationService().prompt_for(brief, hypothesis)

    assert prompt.language == "en"
    assert "Marketplace hero image" in prompt.sora_prompt
    assert "Generate one square" in prompt.gpt_image_prompt
    assert "--ar 1:1" in prompt.midjourney_prompt
    assert prompt.russian_text_blocks
    assert all("Главная" in block or "Проверить" in block for block in prompt.russian_text_blocks)
    assert prompt.draft_only is True


def test_prompt_generation_creates_prompt_per_hypothesis() -> None:
    service = ContentCTRService()
    brief = service.build_brief({"sku": "SKU-PROMPTS"})
    hypotheses = service.generate_hypotheses(brief)[:3]

    prompts = PromptGenerationService().generate_prompts(brief, hypotheses)

    assert len(prompts) == 3
    assert all(prompt.mock_mode for prompt in prompts)

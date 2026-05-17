import pytest

from zentory.agents.content_agent import ContentAgent
from zentory.core.enums import RiskLevel
from zentory.schemas.content import ContentDraftStatus
from zentory.services.content_generation_service import (
    ContentGenerationService,
    MockContentLLMProvider,
)


@pytest.mark.asyncio
async def test_content_agent_generates_draft_card_for_minimal_brief() -> None:
    agent = ContentAgent()

    analysis = await agent.analyze(
        {
            "event_type": "content_brief",
            "payload": {
                "marketplace": "wildberries",
                "category": "кухонная техника",
                "product_name": "вакууматор для продуктов",
                "brand": "Zentory Home",
                "article": "VAC-FOOD-001",
                "price": 3490,
                "main_characteristics": {"мощность": "110 Вт"},
                "customer_pains": ["продукты быстро портятся"],
                "competitors": ["Kitfort"],
                "marketplace_restrictions": ["не обещать невозможное"],
            },
        }
    )

    draft = analysis["draft"]
    assert analysis["mock"] is True
    assert draft["status"] == ContentDraftStatus.DRAFT
    assert draft["requires_approval"] is True
    assert "вакууматор для продуктов" in draft["seo_title"]
    assert draft["infographic_tasks"]
    assert draft["photo_tasks"]
    assert draft["video_tasks"]
    assert draft["keywords"]
    assert draft["pre_publish_checklist"]


@pytest.mark.asyncio
async def test_content_agent_creates_approval_action_before_apply() -> None:
    agent = ContentAgent()

    actions = await agent.propose_actions(
        {"event_type": "content_new", "payload": {"product_name": "вакууматор для продуктов"}}
    )

    assert any(action.action_type == "content_card_draft_created" for action in actions)
    approval_actions = [
        action for action in actions if action.action_type == "content_apply_requires_approval"
    ]
    assert approval_actions
    assert approval_actions[0].risk_level == RiskLevel.HIGH
    assert approval_actions[0].payload["requires_approval"] is True
    assert approval_actions[0].payload["draft_mode"] is True


@pytest.mark.asyncio
async def test_content_generation_service_uses_replaceable_mock_provider() -> None:
    service = ContentGenerationService(provider=MockContentLLMProvider())
    brief = service.build_mock_brief(sku="SKU-CONTENT-1")

    draft = await service.generate_draft(brief)

    assert draft.llm_provider == "mock"
    assert draft.mock is True
    assert draft.sku == "SKU-CONTENT-1"

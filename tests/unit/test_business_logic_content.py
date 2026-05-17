import pytest

from zentory.actions.schemas import Action
from zentory.core.enums import ApprovalMode
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.safety_engine import SafetyEngine
from zentory.schemas.content import ContentDraftStatus
from zentory.services.content_generation_service import ContentGenerationService


@pytest.mark.asyncio
async def test_generated_card_changes_are_draft_and_require_approval() -> None:
    service = ContentGenerationService()
    draft = await service.generate_draft(service.build_mock_brief("SKU-CONTENT-1"))

    assert draft.status == ContentDraftStatus.DRAFT
    assert draft.requires_approval is True
    assert draft.mock is True


def test_content_cannot_be_published_automatically() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="content_publish",
        title="Publish marketplace card",
        description="Publishing card content must never be automatic",
        payload={"sku": "SKU-CONTENT-1"},
    )

    decision = engine.evaluate(action)

    assert decision.requires_approval is True
    assert decision.allowed_to_execute is False


def test_card_publication_requires_approval() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="content_card_publish",
        title="Publish edited card",
        description="Marketplace card publish audit",
        payload={"sku": "SKU-CONTENT-1", "status": "pending_publish"},
    )

    decision = engine.evaluate(action)

    assert decision.approval_mode in {ApprovalMode.SOFT_APPROVAL, ApprovalMode.HARD_APPROVAL}
    assert decision.requires_approval is True
    assert decision.allowed_to_execute is False


def test_mass_content_change_requires_hard_approval() -> None:
    engine = SafetyEngine(mode=AutomationMode.AUTO)
    action = Action(
        action_type="content_bulk_update",
        title="Bulk edit marketplace cards",
        description="Mass content update audit",
        payload={"sku_count": 50, "fields": ["title", "description"]},
    )

    decision = engine.evaluate(action)

    assert decision.approval_mode == ApprovalMode.HARD_APPROVAL
    assert decision.requires_hard_approval is True
    assert decision.allowed_to_execute is False

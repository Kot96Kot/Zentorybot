import pytest

from zentory.agents.feedback_agent import FeedbackAgent
from zentory.core.enums import ApprovalMode


@pytest.mark.asyncio
async def test_typical_question_can_create_draft() -> None:
    actions = await FeedbackAgent().propose_actions(
        {
            "event_type": "feedback",
            "payload": {"kind": "question", "text": "Подходит ли к модели X?"},
        }
    )

    assert actions
    assert actions[0].action_type == "feedback_reply_draft"
    assert actions[0].payload["mock"] is True


@pytest.mark.asyncio
@pytest.mark.xfail(
    strict=True, reason="FeedbackAgent does not classify negative reviews as approval-gated"
)
async def test_negative_review_requires_approval() -> None:
    actions = await FeedbackAgent().propose_actions(
        {
            "event_type": "feedback",
            "payload": {"kind": "review", "rating": 1, "text": "Ужасное качество"},
        }
    )

    assert actions[0].approval_mode != ApprovalMode.NONE


@pytest.mark.asyncio
@pytest.mark.xfail(
    strict=True, reason="FeedbackAgent does not escalate complaint/warranty/return/legal risk"
)
async def test_complaint_warranty_return_or_legal_risk_requires_hard_approval() -> None:
    actions = await FeedbackAgent().propose_actions(
        {
            "event_type": "feedback",
            "payload": {
                "kind": "review",
                "rating": 1,
                "text": "Требую возврат, гарантию и юридическую претензию",
                "risk_tags": ["complaint", "warranty", "return", "legal"],
            },
        }
    )

    assert actions[0].approval_mode == ApprovalMode.HARD_APPROVAL


@pytest.mark.asyncio
@pytest.mark.xfail(
    strict=True, reason="There is no knowledge-base grounding guard for feedback replies"
)
async def test_bot_does_not_promise_facts_missing_from_knowledge_base() -> None:
    actions = await FeedbackAgent().propose_actions(
        {
            "event_type": "feedback",
            "payload": {
                "kind": "question",
                "text": "Есть ли пожизненная гарантия?",
                "knowledge_base": {"warranty": "12 months"},
            },
        }
    )

    assert "пожизн" not in actions[0].description.lower()
    assert actions[0].payload.get("grounded_in_knowledge_base") is True

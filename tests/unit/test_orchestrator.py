import pytest

from zentory.agents.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_orchestrator_accepts_event_and_returns_proposed_actions() -> None:
    orchestrator = Orchestrator()

    decision = await orchestrator.handle_event(
        {"event_type": "daily_digest", "payload": {"mock": True}}
    )

    assert decision.proposed_actions
    assert all(action.payload["mock"] is True for action in decision.proposed_actions)

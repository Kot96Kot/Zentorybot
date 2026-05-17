from fastapi.testclient import TestClient

from zentory.app.main import create_app


def test_action_center_routes_cover_full_mock_lifecycle() -> None:
    client = TestClient(create_app())

    created = client.post(
        "/actions",
        json={
            "agent_name": "AdsAgent",
            "action_type": "ad_bid_change",
            "title": "Increase bid for top keyword",
            "description": "CTR is healthy and campaign needs impressions",
            "before_state": {"bid": 100},
            "after_state": {"bid": 108},
            "risk_level": "LOW",
            "approval_mode": "SOFT_APPROVAL",
            "rollback_available": True,
            "explanation": "Stock is healthy and ACOS is below target",
            "evidence": [{"source": "ads", "label": "acos", "value": "12%"}],
        },
    )

    assert created.status_code == 200
    action = created.json()["action"]
    action_id = action["action_id"]
    assert action["status"] == "proposed"

    preview = client.get(f"/actions/{action_id}/preview")
    assert preview.status_code == 200
    assert preview.json()["preview"]["changes"]["bid"] == {"before": 100, "after": 108}

    blocked_execution = client.post(f"/actions/{action_id}/execute")
    assert blocked_execution.status_code == 200
    assert blocked_execution.json()["action"]["status"] == "proposed"

    approved = client.post(f"/actions/{action_id}/approve", params={"approved_by": "owner"})
    assert approved.status_code == 200
    assert approved.json()["action"]["status"] == "approved"

    executed = client.post(f"/actions/{action_id}/execute")
    assert executed.status_code == 200
    assert executed.json()["action"]["status"] == "executed"
    assert executed.json()["action"]["payload"]["external_api_called"] is False

    rolled_back = client.post(f"/actions/{action_id}/rollback")
    assert rolled_back.status_code == 200
    assert rolled_back.json()["action"]["status"] == "rolled_back"


def test_action_center_routes_return_404_for_missing_action() -> None:
    client = TestClient(create_app())

    response = client.get("/actions/missing-action-id/preview")

    assert response.status_code == 404
    assert "missing-action-id" in response.json()["detail"]

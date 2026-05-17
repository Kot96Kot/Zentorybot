from pathlib import Path

from fastapi.testclient import TestClient

from zentory.actions.action_center import ActionCenter
from zentory.app.main import create_app
from zentory.core.enums import ActionStatus, ApprovalMode, RiskLevel


def test_mvp_demo_required_endpoints_are_available() -> None:
    client = TestClient(create_app())

    checks = [
        ("GET", "/health"),
        ("GET", "/ready"),
        ("GET", "/reports/daily"),
        ("GET", "/sku/WB-MOCK-1/intelligence"),
        ("GET", "/analytics/abc"),
        ("GET", "/analytics/forecast"),
        ("GET", "/supply/risks"),
        ("GET", "/finance/check"),
        ("GET", "/learning/actions"),
    ]

    for method, path in checks:
        response = client.get(path) if method == "GET" else client.post(path)
        assert response.status_code == 200, path

    webhook = client.post("/telegram/webhook", json={"text": "/daily"})
    assert webhook.status_code == 200
    assert webhook.json()["mock"] is True


def test_mvp_demo_telegram_commands_return_mock_responses() -> None:
    client = TestClient(create_app())
    commands = [
        "/daily",
        "/alerts",
        "/sku WB-MOCK-1",
        "/plan",
        "/status",
        "/abc",
        "/forecast",
        "/stock_risks",
        "/content_sku WB-MOCK-1",
        "/finance_check",
    ]

    for command in commands:
        response = client.post("/telegram/webhook", json={"text": command})
        body = response.json()
        assert response.status_code == 200, command
        assert body["mock"] is True, command
        assert body["status"] == "ok", command

    plan = client.post("/telegram/webhook", json={"text": "/plan"}).json()
    action_id = plan["decision"]["proposed_actions"][0]["action_id"]
    approve = client.post("/telegram/webhook", json={"text": f"/approve {action_id}"})
    reject = client.post("/telegram/webhook", json={"text": f"/reject {action_id}"})
    rollback = client.post("/telegram/webhook", json={"text": f"/rollback {action_id}"})

    assert approve.status_code == 200
    assert approve.json()["mock"] is True
    assert reject.status_code == 200
    assert reject.json()["mock"] is True
    assert rollback.status_code == 200
    assert rollback.json()["mock"] is True


def test_mvp_demo_safety_and_secret_guards() -> None:
    center = ActionCenter()
    risky = center.create_action(
        agent_name="SafetyAudit",
        action_type="price_change",
        title="High-risk price change",
        description="MVP demo guard",
        risk_level=RiskLevel.HIGH,
        approval_mode=ApprovalMode.NONE,
    )

    executed = center.execute_action(risky.action_id)

    assert risky.approval_mode == ApprovalMode.HARD_APPROVAL
    assert executed.status != ActionStatus.EXECUTED
    assert executed.payload.get("external_api_called") is None
    assert not Path(".env").exists()
    assert Path(".env.example").exists()

from fastapi.testclient import TestClient

from zentory.app.main import create_app


def test_app_boot_and_reports_daily() -> None:
    client = TestClient(create_app())

    response = client.get("/reports/daily")

    assert response.status_code == 200
    assert response.json()["mock"] is True


def test_telegram_webhook_returns_actions() -> None:
    client = TestClient(create_app())

    response = client.post("/telegram/webhook", json={"event_type": "feedback", "text": "mock"})

    assert response.status_code == 200
    assert response.json()["proposed_actions"]

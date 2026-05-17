from fastapi.testclient import TestClient

from zentory.app.main import create_app


def test_dashboard_overview_renders_mock_cards() -> None:
    client = TestClient(create_app())

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Статус системы" in response.text
    assert "Режим безопасности" in response.text
    assert "Топ SKU с рисками" in response.text
    assert "Состояние агентов" in response.text


def test_dashboard_alerts_renders_attention_items() -> None:
    client = TestClient(create_app())

    response = client.get("/dashboard/alerts")

    assert response.status_code == 200
    assert "WB-MOCK-1" in response.text
    assert "critical" in response.text


def test_dashboard_actions_renders_approval_table() -> None:
    client = TestClient(create_app())

    response = client.get("/dashboard/actions")

    assert response.status_code == 200
    assert "act-ads-007" in response.text
    assert "SOFT_APPROVAL" in response.text


def test_dashboard_sku_renders_sku_details() -> None:
    client = TestClient(create_app())

    response = client.get("/dashboard/sku/WB-MOCK-1")

    assert response.status_code == 200
    assert "SKU WB-MOCK-1" in response.text
    assert "Отзывы" in response.text
    assert "Реклама" in response.text


def test_dashboard_agents_and_audit_render() -> None:
    client = TestClient(create_app())

    agents = client.get("/dashboard/agents")
    audit = client.get("/dashboard/audit")

    assert agents.status_code == 200
    assert "InventoryAgent" in agents.text
    assert audit.status_code == 200
    assert "safety_action_evaluated" in audit.text

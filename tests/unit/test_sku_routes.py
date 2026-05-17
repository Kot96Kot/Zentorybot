from fastapi.testclient import TestClient

from zentory.app.main import create_app


def test_sku_intelligence_endpoint_returns_card_contract() -> None:
    client = TestClient(create_app())

    response = client.get("/sku/WB-MOCK-1/intelligence")

    assert response.status_code == 200
    body = response.json()
    assert body["mock"] is True
    assert body["basic"]["sku"] == "WB-MOCK-1"
    assert body["basic"]["nm_id"] == 1234567
    assert body["sales"]["sales_qty_day"] == 18
    assert body["stock"]["stock_by_warehouse"]["Коледино"] == 41
    assert body["advertising"]["campaign_status"] == "limited_by_stock"
    assert body["conversion"]["click_to_order"] == 2.6
    assert body["reputation"]["unanswered_questions"] == 4
    assert body["competitor"]["where_we_are_weaker"]
    assert body["risks"]["out_of_stock"] is True
    assert body["recommendations"][0]["approval_required"] is True


def test_dashboard_sku_uses_sku_intelligence_card_structure() -> None:
    client = TestClient(create_app())

    response = client.get("/dashboard/sku/WB-MOCK-1")

    assert response.status_code == 200
    assert "SKU WB-MOCK-1" in response.text
    assert "SKU Intelligence Card" in response.text
    assert "nm_id" in response.text
    assert "Реклама" in response.text
    assert "Конкуренты" in response.text
    assert "Рекомендации" in response.text

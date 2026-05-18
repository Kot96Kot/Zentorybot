from fastapi.testclient import TestClient

from zentory.app.main import create_app


def test_platform_modules_endpoint_returns_all_modules() -> None:
    client = TestClient(create_app())

    response = client.get("/platform/modules")

    assert response.status_code == 200
    data = response.json()
    assert data["mock"] is True
    assert data["summary"]["forecast_items"] == 3
    assert "forecast_abc" in data["modules"]
    assert "data_contracts" in data["modules"]


def test_platform_leaf_endpoints_are_read_only_mock_reports() -> None:
    client = TestClient(create_app())

    for path in (
        "/platform/forecast-abc",
        "/platform/supply-localization",
        "/platform/content-ctr",
        "/platform/finance-checker",
        "/platform/learning-loop",
        "/platform/data-contracts",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()["mock"] is True

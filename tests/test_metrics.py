from fastapi.testclient import TestClient


def test_metrics_returns_200(client: TestClient):
    response = client.get("/metrics")
    assert response.status_code == 200


def test_metrics_content_type_is_text_plain(client: TestClient):
    response = client.get("/metrics")
    assert "text/plain" in response.headers["content-type"]


def test_metrics_contains_incidents_processed_total(client: TestClient):
    response = client.get("/metrics")
    assert "incidents_processed_total" in response.text


def test_metrics_contains_analysis_duration_seconds(client: TestClient):
    response = client.get("/metrics")
    assert "analysis_duration_seconds" in response.text

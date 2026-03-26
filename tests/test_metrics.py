from unittest.mock import patch
from uuid import UUID

from fastapi.testclient import TestClient

from incident_lens.analyzer import Analysis


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


def test_incidents_processed_total_increments_after_analysis(
    client: TestClient, patch_job_session, mock_analysis_result: Analysis
):
    from incident_lens.jobs import run_analysis

    response = client.post(
        "/incidents",
        json={"service_name": "auth-service", "alert_type": "high_error_rate"},
    )
    assert response.status_code == 201
    incident_id = response.json()["id"]

    with patch("incident_lens.jobs.analyze", return_value=mock_analysis_result):
        run_analysis(UUID(incident_id))

    metrics_response = client.get("/metrics")
    assert "incidents_processed_total" in metrics_response.text
    lines = metrics_response.text.splitlines()
    metric_line = next(l for l in lines if l.startswith("incidents_processed_total"))
    assert float(metric_line.split()[-1]) >= 1

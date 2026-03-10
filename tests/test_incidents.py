from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from incident_lens.jobs import run_analysis


def test_create_incident_returns_201(client: TestClient):
    response = client.post(
        "/incidents",
        json={"service_name": "auth-service", "alert_type": "high_error_rate"},
    )
    assert response.status_code == 201


def test_create_incident_response_fields(client: TestClient):
    response = client.post(
        "/incidents",
        json={"service_name": "auth-service", "alert_type": "high_error_rate"},
    )
    body = response.json()
    assert body["service_name"] == "auth-service"
    assert body["alert_type"] == "high_error_rate"
    assert body["status"] == "pending"
    assert "id" in body
    assert "created_at" in body


def test_create_incident_missing_required_fields_returns_422(client: TestClient):
    response = client.post("/incidents", json={})
    assert response.status_code == 422


def test_created_incident_is_retrievable(client: TestClient):
    create_response = client.post(
        "/incidents",
        json={"service_name": "auth-service", "alert_type": "high_error_rate"},
    )
    incident_id = create_response.json()["id"]

    get_response = client.get(f"/incidents/{incident_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == incident_id


def test_get_nonexistent_incident_returns_404(client: TestClient):
    response = client.get("/incidents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_incident_enqueues_analysis_job(client: TestClient, mock_queue: MagicMock):
    response = client.post(
        "/incidents",
        json={"service_name": "auth-service", "alert_type": "high_error_rate"},
    )
    incident_id = response.json()["id"]
    mock_queue.assert_called_once_with(run_analysis, incident_id)

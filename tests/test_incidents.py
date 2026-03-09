from fastapi.testclient import TestClient

from incident_lens.main import app

client = TestClient(app)


def test_create_incident_returns_201():
    response = client.post(
        "/incidents",
        json={"service_name": "auth-service", "alert_type": "high_error_rate"},
    )
    assert response.status_code == 201


def test_create_incident_response_fields():
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


def test_create_incident_missing_required_fields_returns_422():
    response = client.post("/incidents", json={})
    assert response.status_code == 422

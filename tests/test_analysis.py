from unittest.mock import patch
from uuid import UUID

from fastapi.testclient import TestClient

from incident_lens.analyzer import _Analysis
from incident_lens.metrics import incidents_processed_total
from incident_lens.models import IncidentAnalysis, IncidentModel


def _create_incident(client: TestClient) -> str:
    response = client.post(
        "/incidents",
        json={"service_name": "auth-service", "alert_type": "high_error_rate"},
    )
    return response.json()["id"]


def test_get_analysis_returns_404_when_not_available(client: TestClient):
    incident_id = _create_incident(client)
    response = client.get(f"/incidents/{incident_id}/analysis")
    assert response.status_code == 404


def test_get_analysis_returns_result_when_available(client: TestClient):
    from incident_lens.api import app
    from incident_lens.database import get_db

    incident_id = _create_incident(client)

    db = next(app.dependency_overrides[get_db]())
    incident = db.get(IncidentModel, UUID(incident_id))
    db.add(
        IncidentAnalysis(
            incident_id=incident.id,
            summary="High error rate detected in auth-service.",
            suspected_service="auth-service",
            confidence=0.95,
            recommendations=["Check recent deployments", "Review error logs"],
        )
    )
    db.commit()

    response = client.get(f"/incidents/{incident_id}/analysis")
    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == incident_id
    assert body["summary"] == "High error rate detected in auth-service."
    assert body["suspected_service"] == "auth-service"
    assert body["confidence"] == 0.95
    assert body["recommendations"] == ["Check recent deployments", "Review error logs"]


def test_run_analysis_job_calls_analyzer_and_stores_result(client: TestClient, patch_job_session):
    from incident_lens.api import app
    from incident_lens.database import get_db
    from incident_lens.jobs import run_analysis

    incident_id = _create_incident(client)

    mock_result = _Analysis(
        summary="Auth service is failing.",
        suspected_service="auth-service",
        confidence=0.9,
        recommendations=["Restart the service"],
    )

    with patch("incident_lens.jobs.analyze", return_value=mock_result):
        run_analysis(UUID(incident_id))

    db = next(app.dependency_overrides[get_db]())
    analysis = db.query(IncidentAnalysis).filter_by(incident_id=UUID(incident_id)).first()
    assert analysis is not None
    assert analysis.summary == "Auth service is failing."
    assert analysis.confidence == 0.9


def test_run_analysis_increments_counter(client: TestClient, patch_job_session):
    from incident_lens.jobs import run_analysis

    incident_id = _create_incident(client)

    mock_result = _Analysis(
        summary="Auth service is failing.",
        suspected_service="auth-service",
        confidence=0.9,
        recommendations=["Restart the service"],
    )

    before = incidents_processed_total._value.get()

    with patch("incident_lens.jobs.analyze", return_value=mock_result):
        run_analysis(UUID(incident_id))

    after = incidents_processed_total._value.get()
    assert after - before == 1

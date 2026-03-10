from uuid import UUID

from incident_lens.analyzer import analyze
from incident_lens.database import SessionLocal
from incident_lens.models import IncidentAnalysis, IncidentModel


def run_analysis(incident_id: UUID) -> None:
    with SessionLocal() as db:
        incident = db.get(IncidentModel, incident_id)
        if incident is None:
            return

        incident.status = "analyzing"
        db.commit()

        logs = [log.message for log in incident.logs]
        result = analyze(logs, incident.service_name, incident.alert_type)

        db.add(
            IncidentAnalysis(
                incident_id=incident.id,
                summary=result.summary,
                suspected_service=result.suspected_service,
                confidence=result.confidence,
                recommendations=result.recommendations,
            )
        )
        incident.status = "resolved"
        db.commit()

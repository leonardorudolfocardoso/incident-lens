from incident_lens.database import SessionLocal
from incident_lens.models import IncidentModel


def run_analysis(incident_id: str) -> None:
    with SessionLocal() as db:
        incident = db.get(IncidentModel, incident_id)
        if incident is None:
            return

        incident.status = "analyzing"
        db.commit()

        # TODO: call analyzer and store results

        incident.status = "resolved"
        db.commit()

import time
from uuid import UUID

from incident_lens.analyzer import analyze
from incident_lens.database import SessionLocal
from incident_lens.logging_config import get_logger
from incident_lens.metrics import analysis_duration_seconds, incidents_processed_total
from incident_lens.models import IncidentAnalysis, IncidentModel

logger = get_logger(__name__)


def run_analysis(incident_id: UUID) -> None:
    with SessionLocal() as db:
        incident = db.get(IncidentModel, incident_id)
        if incident is None:
            logger.warning("incident_not_found", incident_id=str(incident_id))
            return

        incident.status = "analyzing"
        db.commit()

        logs = [log.message for log in incident.logs]

        try:
            start = time.perf_counter()
            result = analyze(logs, incident.service_name, incident.alert_type)
            processing_time = time.perf_counter() - start
        except Exception:
            logger.error(
                "analysis_failed",
                incident_id=str(incident_id),
                analysis_status="failed",
                exc_info=True,
            )
            raise

        analysis_duration_seconds.observe(processing_time)
        incidents_processed_total.inc()

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

        logger.info(
            "analysis_complete",
            incident_id=str(incident_id),
            processing_time=processing_time,
            analysis_status="resolved",
            confidence=result.confidence,
        )

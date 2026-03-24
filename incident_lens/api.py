from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from incident_lens.database import get_db
from incident_lens.jobs import run_analysis
from incident_lens.logging_config import configure_logging, get_logger
from incident_lens.models import IncidentAnalysis, IncidentLogModel, IncidentModel, IncidentStatus
from incident_lens.queue import queue

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="IncidentLens")


class IncidentLog(BaseModel):
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IncidentCreate(BaseModel):
    service_name: str
    alert_type: str
    logs: list[IncidentLog] = Field(default_factory=list)


class Incident(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_name: str
    alert_type: str
    status: IncidentStatus
    created_at: datetime


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    incident_id: UUID
    summary: str
    suspected_service: str
    confidence: float
    recommendations: list[str]


@app.post("/incidents", response_model=Incident, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)) -> Incident:
    incident = IncidentModel(
        service_name=payload.service_name,
        alert_type=payload.alert_type,
        logs=[
            IncidentLogModel(message=log.message, timestamp=log.timestamp)
            for log in payload.logs
        ],
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    queue.enqueue(run_analysis, incident.id)
    logger.info(
        "incident_created",
        incident_id=str(incident.id),
        service_name=incident.service_name,
        alert_type=incident.alert_type,
    )
    return Incident.model_validate(incident)


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: UUID, db: Session = Depends(get_db)) -> Incident:
    incident = db.get(IncidentModel, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return Incident.model_validate(incident)


@app.get("/incidents/{incident_id}/analysis", response_model=AnalysisResponse)
def get_analysis(incident_id: UUID, db: Session = Depends(get_db)) -> AnalysisResponse:
    from sqlalchemy import select

    analysis = db.scalar(
        select(IncidentAnalysis).where(IncidentAnalysis.incident_id == incident_id)
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    return AnalysisResponse.model_validate(analysis)

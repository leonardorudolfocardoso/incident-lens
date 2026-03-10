from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from incident_lens.database import get_db
from incident_lens.jobs import run_analysis
from incident_lens.models import IncidentLogModel, IncidentModel
from incident_lens.queue import queue

app = FastAPI(title="IncidentLens")


class IncidentStatus(str, Enum):
    pending = "pending"
    analyzing = "analyzing"
    resolved = "resolved"


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
    queue.enqueue(run_analysis, str(incident.id))
    return Incident.model_validate(incident)


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: UUID, db: Session = Depends(get_db)) -> Incident:
    incident = db.get(IncidentModel, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return Incident.model_validate(incident)

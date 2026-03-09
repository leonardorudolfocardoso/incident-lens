from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="IncidentLens")

# In-memory store — will be replaced with PostgreSQL
_incidents: dict = {}


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
    id: UUID
    service_name: str
    alert_type: str
    status: IncidentStatus
    created_at: datetime


@app.post("/incidents", response_model=Incident, status_code=201)
def create_incident(payload: IncidentCreate) -> Incident:
    incident = Incident(
        id=uuid4(),
        service_name=payload.service_name,
        alert_type=payload.alert_type,
        status=IncidentStatus.pending,
        created_at=datetime.now(timezone.utc),
    )
    _incidents[incident.id] = incident
    # TODO: persist to DB and enqueue analysis job
    return incident


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(incident_id: UUID) -> Incident:
    incident = _incidents.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

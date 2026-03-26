from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from incident_lens.database import Base


class IncidentStatus(str, Enum):
    pending = "pending"
    analyzing = "analyzing"
    resolved = "resolved"


class IncidentModel(Base):
    __tablename__ = "incidents"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    service_name: Mapped[str] = mapped_column(String)
    alert_type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default=IncidentStatus.pending)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    logs: Mapped[list["IncidentLogModel"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )


class IncidentLogModel(Base):
    __tablename__ = "incident_logs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    message: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    incident: Mapped["IncidentModel"] = relationship(back_populates="logs")


class IncidentAnalysis(Base):
    __tablename__ = "incident_analysis"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"), unique=True)
    summary: Mapped[str] = mapped_column(String)
    suspected_service: Mapped[str] = mapped_column(String)
    confidence: Mapped[float]
    recommendations: Mapped[list] = mapped_column(JSON)

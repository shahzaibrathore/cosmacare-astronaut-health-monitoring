"""SQLAlchemy ORM models for crew, telemetry and alerts."""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class CrewMember(Base):
    __tablename__ = "crew_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False, default="Mission Specialist")
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    telemetry_records = relationship(
        "TelemetryRecord", back_populates="crew", cascade="all, delete-orphan"
    )
    alerts = relationship(
        "AlertLog", back_populates="crew", cascade="all, delete-orphan"
    )


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crew_members.id"), nullable=False, index=True)
    heart_rate = Column(Integer, nullable=False)
    spo2 = Column(Float, nullable=False)
    body_temp = Column(Float, nullable=False)
    systolic_bp = Column(Integer, nullable=False)
    diastolic_bp = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, index=True)

    crew = relationship("CrewMember", back_populates="telemetry_records")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crew_members.id"), nullable=False, index=True)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    parameter = Column(String, nullable=True)
    acknowledged = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, index=True)

    crew = relationship("CrewMember", back_populates="alerts")
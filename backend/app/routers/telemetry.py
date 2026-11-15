"""Telemetry ingestion and query endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.engine import evaluate_telemetry
from app.models import CrewMember, TelemetryRecord
from app.schemas import TelemetryCreate, TelemetryResponse

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post(
    "/",
    response_model=TelemetryResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_telemetry(
    payload: TelemetryCreate,
    db: Session = Depends(get_db),
):
    try:
        crew = (
            db.query(CrewMember)
            .filter(CrewMember.id == payload.crew_id)
            .first()
        )

        if not crew:
            if not settings.enable_auto_seed:
                raise HTTPException(
                    status_code=404,
                    detail=f"Crew member {payload.crew_id} not found",
                )

            crew = CrewMember(
                id=payload.crew_id,
                name=f"Astronaut-{payload.crew_id}",
                role="Mission Specialist",
            )
            db.add(crew)
            db.flush()

        record = TelemetryRecord(
            crew_id=payload.crew_id,
            heart_rate=payload.heart_rate,
            spo2=payload.spo2,
            body_temp=payload.body_temp,
            systolic_bp=payload.systolic_bp,
            diastolic_bp=payload.diastolic_bp,
        )

        db.add(record)
        db.flush()

        evaluate_telemetry(payload, db)

        db.commit()
        db.refresh(record)

        return record

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.get("/{crew_id}", response_model=List[TelemetryResponse])
def get_telemetry(
    crew_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if crew_id < 1:
        raise HTTPException(
            status_code=422,
            detail="Crew ID must be greater than zero",
        )

    return (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.crew_id == crew_id)
        .order_by(
            TelemetryRecord.timestamp.desc(),
            TelemetryRecord.id.desc(),
        )
        .limit(limit)
        .all()
    )

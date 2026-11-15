"""Alert listing and acknowledgement endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlertLog
from app.schemas import AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    crew_id: Optional[int] = Query(default=None, ge=1),
    acknowledged: Optional[bool] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(AlertLog)

    if crew_id is not None:
        query = query.filter(AlertLog.crew_id == crew_id)

    if acknowledged is not None:
        query = query.filter(AlertLog.acknowledged == acknowledged)

    return query.order_by(
        AlertLog.timestamp.desc(),
        AlertLog.id.desc(),
    ).limit(limit).all()


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    if alert_id < 1:
        raise HTTPException(
            status_code=422,
            detail="Alert ID must be greater than zero",
        )

    alert = db.query(AlertLog).filter(
        AlertLog.id == alert_id
    ).first()

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    try:
        alert.acknowledged = True
        db.commit()
        db.refresh(alert)
        return alert

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to acknowledge alert due to a database error",
        )

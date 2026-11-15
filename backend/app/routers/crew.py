"""Crew member management endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CrewMember
from app.schemas import CrewCreate, CrewResponse

router = APIRouter(prefix="/crew", tags=["crew"])


@router.post("/", response_model=CrewResponse, status_code=status.HTTP_201_CREATED)
def create_crew(payload: CrewCreate, db: Session = Depends(get_db)):
    existing = db.query(CrewMember).filter(
        CrewMember.name == payload.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Crew member '{payload.name}' already exists",
        )

    crew = CrewMember(name=payload.name, role=payload.role)

    try:
        db.add(crew)
        db.commit()
        db.refresh(crew)
        return crew

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Crew member '{payload.name}' already exists",
        )


@router.get("/", response_model=List[CrewResponse])
def list_crew(db: Session = Depends(get_db)):
    return db.query(CrewMember).order_by(CrewMember.id).all()


@router.get("/{crew_id}", response_model=CrewResponse)
def get_crew(crew_id: int, db: Session = Depends(get_db)):
    crew = db.query(CrewMember).filter(CrewMember.id == crew_id).first()

    if not crew:
        raise HTTPException(status_code=404, detail="Crew member not found")

    return crew

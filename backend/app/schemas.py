"""Pydantic v2 validation schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CrewCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="Mission Specialist", max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot contain only whitespace")
        return value.strip()


class CrewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role: str
    created_at: datetime


class TelemetryCreate(BaseModel):
    crew_id: int = Field(..., ge=1, description="Unique ID of the astronaut")
    heart_rate: int = Field(..., ge=30, le=220, description="Heart Rate in BPM")
    spo2: float = Field(..., ge=50.0, le=100.0, description="Blood oxygen %")
    body_temp: float = Field(..., ge=30.0, le=43.0, description="Core body temp °C")
    systolic_bp: int = Field(..., ge=60, le=250, description="Systolic BP mmHg")
    diastolic_bp: int = Field(..., ge=40, le=150, description="Diastolic BP mmHg")


class TelemetryResponse(TelemetryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crew_id: int
    severity: str
    message: str
    parameter: Optional[str] = None
    acknowledged: bool
    timestamp: datetime

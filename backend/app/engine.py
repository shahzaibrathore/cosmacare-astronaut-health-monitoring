"""Deterministic clinical rule evaluation engine."""

from dataclasses import dataclass
from typing import List

from sqlalchemy.orm import Session

from app.models import AlertLog
from app.schemas import TelemetryCreate


THRESHOLDS = {
    "hr_low_critical": 45,
    "hr_low_warning": 50,
    "hr_high_warning": 150,
    "hr_high_critical": 160,
    "spo2_critical": 90.0,
    "spo2_warning": 94.0,
    "temp_high_warning": 38.5,
    "temp_high_critical": 39.0,
    "temp_low_critical": 35.0,
    "temp_low_warning": 35.5,
    "systolic_low_critical": 80,
    "systolic_high_critical": 160,
    "diastolic_low_critical": 50,
    "diastolic_high_critical": 100,
}


@dataclass
class DetectedAlert:
    severity: str
    parameter: str
    message: str


def _detect_alerts(data: TelemetryCreate) -> List[DetectedAlert]:
    alerts = []
    t = THRESHOLDS

    # Oxygen saturation
    if data.spo2 <= t["spo2_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "spo2",
            f"CRITICAL: Low blood oxygen detected! SpO2 is {data.spo2}%. Hypoxia risk."
        ))
    elif data.spo2 <= t["spo2_warning"]:
        alerts.append(DetectedAlert(
            "WARNING", "spo2",
            f"WARNING: Blood oxygen level is low. SpO2 is {data.spo2}%."
        ))

    # Heart rate
    if data.heart_rate < t["hr_low_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "heart_rate",
            f"CRITICAL: Extremely low heart rate! Heart rate is {data.heart_rate} BPM. Severe bradycardia risk."
        ))
    elif data.heart_rate < t["hr_low_warning"]:
        alerts.append(DetectedAlert(
            "WARNING", "heart_rate",
            f"WARNING: Low heart rate detected. Heart rate is {data.heart_rate} BPM."
        ))
    elif data.heart_rate > t["hr_high_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "heart_rate",
            f"CRITICAL: Extremely high heart rate! Heart rate is {data.heart_rate} BPM. Severe tachycardia risk."
        ))
    elif data.heart_rate > t["hr_high_warning"]:
        alerts.append(DetectedAlert(
            "WARNING", "heart_rate",
            f"WARNING: High heart rate detected. Heart rate is {data.heart_rate} BPM."
        ))

    # Body temperature
    if data.body_temp > t["temp_high_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "body_temp",
            f"CRITICAL: Extremely high body temperature! Temperature is {data.body_temp}°C. Severe fever risk."
        ))
    elif data.body_temp > t["temp_high_warning"]:
        alerts.append(DetectedAlert(
            "WARNING", "body_temp",
            f"WARNING: Elevated body temperature detected. Temperature is {data.body_temp}°C."
        ))
    elif data.body_temp < t["temp_low_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "body_temp",
            f"CRITICAL: Extremely low body temperature! Temperature is {data.body_temp}°C. Hypothermia risk."
        ))
    elif data.body_temp < t["temp_low_warning"]:
        alerts.append(DetectedAlert(
            "WARNING", "body_temp",
            f"WARNING: Low body temperature detected. Temperature is {data.body_temp}°C."
        ))

    # Systolic blood pressure
    if data.systolic_bp < t["systolic_low_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "systolic_bp",
            f"CRITICAL: Low systolic blood pressure! Systolic BP is {data.systolic_bp} mmHg. Hypotension risk."
        ))
    elif data.systolic_bp > t["systolic_high_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "systolic_bp",
            f"CRITICAL: High systolic blood pressure! Systolic BP is {data.systolic_bp} mmHg. Hypertension risk."
        ))

    # Diastolic blood pressure
    if data.diastolic_bp < t["diastolic_low_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "diastolic_bp",
            f"CRITICAL: Low diastolic blood pressure! Diastolic BP is {data.diastolic_bp} mmHg."
        ))
    elif data.diastolic_bp > t["diastolic_high_critical"]:
        alerts.append(DetectedAlert(
            "CRITICAL", "diastolic_bp",
            f"CRITICAL: High diastolic blood pressure! Diastolic BP is {data.diastolic_bp} mmHg."
        ))

    return alerts


def evaluate_telemetry(
    data: TelemetryCreate,
    db: Session,
) -> List[AlertLog]:
    """Add detected alerts to the current transaction.

    This function deliberately does not commit or rollback.
    The caller owns the complete database transaction.
    """
    detected = _detect_alerts(data)
    persisted = []

    for item in detected:
        alert = AlertLog(
            crew_id=data.crew_id,
            severity=item.severity,
            parameter=item.parameter,
            message=item.message,
        )
        db.add(alert)
        persisted.append(alert)

    return persisted

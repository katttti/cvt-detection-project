from fastapi import Depends, FastAPI

from backend.app.auth import verify_access_password
from backend.app.models import (
    GuardianNotification,
    HealthResponse,
    PressureEventCreate,
    PressureEventRecord,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    TransferEventCreate,
    TransferEventRecord,
)
from backend.app.scoring import score_risk
from backend.app.store import store

app = FastAPI(title="CVT Detection Backend", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/v1/pressure-events", response_model=PressureEventRecord, status_code=201)
def create_pressure_event(
    payload: PressureEventCreate,
    _: None = Depends(verify_access_password),
) -> PressureEventRecord:
    event = PressureEventRecord(**payload.model_dump())
    store.pressure_events.append(event)
    return event


@app.post("/v1/transfer-events", response_model=TransferEventRecord, status_code=201)
def create_transfer_event(
    payload: TransferEventCreate,
    _: None = Depends(verify_access_password),
) -> TransferEventRecord:
    event = TransferEventRecord(**payload.model_dump())
    store.transfer_events.append(event)
    return event


@app.post("/v1/risk-assessments", response_model=RiskAssessmentResponse)
def create_risk_assessment(
    payload: RiskAssessmentRequest,
    _: None = Depends(verify_access_password),
) -> RiskAssessmentResponse:
    result = score_risk(
        pressure_score=payload.pressure_score,
        amount=payload.amount,
        is_new_recipient=payload.is_new_recipient,
        hour_of_day=payload.occurred_at.hour,
        recent_urgent_attempts=payload.recent_urgent_attempts,
    )
    assessment = RiskAssessmentResponse(
        profile_id=payload.profile_id,
        pressure_event_id=payload.pressure_event_id,
        transfer_event_id=payload.transfer_event_id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        recommended_action=result.recommended_action,
        reason_codes=result.reason_codes,
    )
    store.risk_assessments.append(assessment)

    if result.risk_level == "red":
        store.guardian_notifications.append(
            GuardianNotification(
                guardian_id=payload.profile_id,
                risk_level=result.risk_level,
                channel="in_app",
                delivery_status="queued",
            )
        )

    return assessment


@app.get("/v1/guardian-notifications", response_model=list[GuardianNotification])
def list_guardian_notifications(
    _: None = Depends(verify_access_password),
) -> list[GuardianNotification]:
    return store.guardian_notifications

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class PressureEventCreate(BaseModel):
    profile_id: UUID
    device_id: UUID
    pressure_score: float = Field(ge=0.0, le=1.0)
    signal_summary: dict[str, object]
    occurred_at: datetime


class PressureEventRecord(PressureEventCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TransferEventCreate(BaseModel):
    profile_id: UUID
    amount: float = Field(gt=0)
    recipient_hash: str
    is_new_recipient: bool
    occurred_at: datetime


class TransferEventRecord(TransferEventCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RiskAssessmentRequest(BaseModel):
    profile_id: UUID
    pressure_event_id: UUID
    transfer_event_id: UUID
    pressure_score: float = Field(ge=0.0, le=1.0)
    amount: float = Field(gt=0)
    is_new_recipient: bool
    occurred_at: datetime
    recent_urgent_attempts: int = Field(default=0, ge=0)


class RiskAssessmentResponse(BaseModel):
    profile_id: UUID
    pressure_event_id: UUID
    transfer_event_id: UUID
    risk_score: float
    risk_level: str
    recommended_action: str
    reason_codes: list[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class GuardianNotification(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    guardian_id: UUID
    risk_level: str
    channel: str
    delivery_status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

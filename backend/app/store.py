import os
from functools import lru_cache
from typing import Any, Protocol
from uuid import UUID

from backend.app.models import (
    GuardianNotification,
    PressureEventCreate,
    PressureEventRecord,
    RiskAssessmentResponse,
    TransferEventCreate,
    TransferEventRecord,
)


class EventStore(Protocol):
    def create_pressure_event(self, payload: PressureEventCreate) -> PressureEventRecord: ...

    def create_transfer_event(self, payload: TransferEventCreate) -> TransferEventRecord: ...

    def create_risk_assessment(self, assessment: RiskAssessmentResponse) -> RiskAssessmentResponse: ...

    def create_guardian_notification(
        self,
        notification: GuardianNotification,
    ) -> GuardianNotification: ...

    def list_guardian_notifications(self) -> list[GuardianNotification]: ...

    def list_active_guardian_ids(self, profile_id: UUID) -> list[UUID]: ...


def _create_supabase_client(url: str, key: str) -> Any:
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError(
            "SUPABASE_URL is configured but the 'supabase' package is not installed."
        ) from exc

    return create_client(url, key)


def _get_first_row(result: Any, table_name: str) -> dict[str, object]:
    rows = getattr(result, "data", None) or []
    if not rows:
        raise RuntimeError(f"{table_name} write returned no rows.")
    return rows[0]


class InMemoryStore:
    def __init__(self) -> None:
        self.pressure_events: list[PressureEventRecord] = []
        self.transfer_events: list[TransferEventRecord] = []
        self.risk_assessments: list[RiskAssessmentResponse] = []
        self.guardian_notifications: list[GuardianNotification] = []

    def create_pressure_event(self, payload: PressureEventCreate) -> PressureEventRecord:
        event = PressureEventRecord(**payload.model_dump())
        self.pressure_events.append(event)
        return event

    def create_transfer_event(self, payload: TransferEventCreate) -> TransferEventRecord:
        event = TransferEventRecord(**payload.model_dump())
        self.transfer_events.append(event)
        return event

    def create_risk_assessment(self, assessment: RiskAssessmentResponse) -> RiskAssessmentResponse:
        self.risk_assessments.append(assessment)
        return assessment

    def create_guardian_notification(
        self,
        notification: GuardianNotification,
    ) -> GuardianNotification:
        self.guardian_notifications.append(notification)
        return notification

    def list_guardian_notifications(self) -> list[GuardianNotification]:
        return list(self.guardian_notifications)

    def list_active_guardian_ids(self, profile_id: UUID) -> list[UUID]:
        # Local development fallback until real guardian links are seeded.
        return [profile_id]


class SupabaseStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def _insert_row(self, table_name: str, payload: dict[str, object]) -> dict[str, object]:
        result = self.client.table(table_name).insert(payload).select("*").execute()
        return _get_first_row(result, table_name)

    def create_pressure_event(self, payload: PressureEventCreate) -> PressureEventRecord:
        row = self._insert_row("pressure_events", payload.model_dump(mode="json"))
        return PressureEventRecord.model_validate(row)

    def create_transfer_event(self, payload: TransferEventCreate) -> TransferEventRecord:
        row = self._insert_row("transfer_events", payload.model_dump(mode="json"))
        return TransferEventRecord.model_validate(row)

    def create_risk_assessment(self, assessment: RiskAssessmentResponse) -> RiskAssessmentResponse:
        row = self._insert_row(
            "risk_assessments",
            assessment.model_dump(mode="json"),
        )
        return RiskAssessmentResponse.model_validate(row)

    def create_guardian_notification(
        self,
        notification: GuardianNotification,
    ) -> GuardianNotification:
        row = self._insert_row(
            "guardian_notifications",
            notification.model_dump(mode="json", exclude_none=True),
        )
        return GuardianNotification.model_validate(row)

    def list_guardian_notifications(self) -> list[GuardianNotification]:
        result = self.client.table("guardian_notifications").select("*").execute()
        rows = getattr(result, "data", None) or []
        return [GuardianNotification.model_validate(row) for row in rows]

    def list_active_guardian_ids(self, profile_id: UUID) -> list[UUID]:
        result = (
            self.client.table("guardian_links")
            .select("guardian_id")
            .eq("teen_id", str(profile_id))
            .eq("status", "active")
            .execute()
        )
        rows = getattr(result, "data", None) or []
        return [UUID(str(row["guardian_id"])) for row in rows]


def build_store() -> EventStore:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if supabase_url and supabase_key:
        return SupabaseStore(_create_supabase_client(supabase_url, supabase_key))
    return InMemoryStore()


@lru_cache(maxsize=1)
def get_store() -> EventStore:
    return build_store()

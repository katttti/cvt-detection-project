from backend.app.models import (
    GuardianNotification,
    PressureEventRecord,
    RiskAssessmentResponse,
    TransferEventRecord,
)


class InMemoryStore:
    def __init__(self) -> None:
        self.pressure_events: list[PressureEventRecord] = []
        self.transfer_events: list[TransferEventRecord] = []
        self.risk_assessments: list[RiskAssessmentResponse] = []
        self.guardian_notifications: list[GuardianNotification] = []


store = InMemoryStore()

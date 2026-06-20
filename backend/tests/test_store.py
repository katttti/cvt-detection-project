from datetime import datetime
from types import SimpleNamespace
from uuid import UUID

from backend.app.models import PressureEventCreate
from backend.app.store import InMemoryStore, SupabaseStore, build_store


class _FakeTable:
    def __init__(self, response_rows: list[dict[str, object]]) -> None:
        self.response_rows = response_rows
        self.insert_payload: dict[str, object] | None = None
        self.selected_columns: str | None = None
        self.filters: list[tuple[str, object]] = []

    def insert(self, payload: dict[str, object]) -> "_FakeTable":
        self.insert_payload = payload
        return self

    def select(self, columns: str = "*") -> "_FakeTable":
        self.selected_columns = columns
        return self

    def eq(self, column: str, value: object) -> "_FakeTable":
        self.filters.append((column, value))
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=self.response_rows)


class _FakeSupabaseClient:
    def __init__(self, tables: dict[str, _FakeTable]) -> None:
        self.tables = tables

    def table(self, table_name: str) -> _FakeTable:
        return self.tables[table_name]


def test_build_store_returns_in_memory_store_when_supabase_env_is_missing(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    store = build_store()

    assert isinstance(store, InMemoryStore)


def test_build_store_returns_supabase_store_when_supabase_env_is_present(monkeypatch):
    fake_client = object()
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setattr("backend.app.store._create_supabase_client", lambda url, key: fake_client)

    store = build_store()

    assert isinstance(store, SupabaseStore)
    assert store.client is fake_client


def test_supabase_store_inserts_pressure_event_and_returns_created_row():
    response_row = {
        "id": "3c1cf734-f34d-4f24-b3c6-f1d09d9bafb7",
        "profile_id": "f6924af8-67a0-4f22-bdb8-1e6fa85339ea",
        "device_id": "4d5d1e72-d3a7-4f91-896c-ab4fcd83f2d6",
        "pressure_score": 0.82,
        "signal_summary": {"urgent_language": True},
        "occurred_at": "2026-06-20T01:13:00+09:00",
        "created_at": "2026-06-20T01:13:05+09:00",
    }
    pressure_table = _FakeTable([response_row])
    store = SupabaseStore(_FakeSupabaseClient({"pressure_events": pressure_table}))
    payload = PressureEventCreate(
        profile_id=UUID("f6924af8-67a0-4f22-bdb8-1e6fa85339ea"),
        device_id=UUID("4d5d1e72-d3a7-4f91-896c-ab4fcd83f2d6"),
        pressure_score=0.82,
        signal_summary={"urgent_language": True},
        occurred_at=datetime.fromisoformat("2026-06-20T01:13:00+09:00"),
    )

    record = store.create_pressure_event(payload)

    assert pressure_table.insert_payload == {
        "profile_id": "f6924af8-67a0-4f22-bdb8-1e6fa85339ea",
        "device_id": "4d5d1e72-d3a7-4f91-896c-ab4fcd83f2d6",
        "pressure_score": 0.82,
        "signal_summary": {"urgent_language": True},
        "occurred_at": "2026-06-20T01:13:00+09:00",
    }
    assert pressure_table.selected_columns == "*"
    assert record.id == UUID("3c1cf734-f34d-4f24-b3c6-f1d09d9bafb7")


def test_supabase_store_lists_only_active_guardian_ids():
    guardian_links_table = _FakeTable(
        [
            {"guardian_id": "2f3b7097-c0fe-4797-a4f2-f8c477ab25ba"},
            {"guardian_id": "7e95c6fb-12dd-403a-ac77-fb45da8a4d18"},
        ]
    )
    store = SupabaseStore(_FakeSupabaseClient({"guardian_links": guardian_links_table}))
    teen_id = UUID("f6924af8-67a0-4f22-bdb8-1e6fa85339ea")

    guardian_ids = store.list_active_guardian_ids(teen_id)

    assert guardian_links_table.selected_columns == "guardian_id"
    assert guardian_links_table.filters == [
        ("teen_id", "f6924af8-67a0-4f22-bdb8-1e6fa85339ea"),
        ("status", "active"),
    ]
    assert guardian_ids == [
        UUID("2f3b7097-c0fe-4797-a4f2-f8c477ab25ba"),
        UUID("7e95c6fb-12dd-403a-ac77-fb45da8a4d18"),
    ]

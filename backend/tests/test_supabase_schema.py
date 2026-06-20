from pathlib import Path


MIGRATION_PATH = Path("supabase/migrations/20260620_create_cvt_core_schema.sql")


def test_supabase_core_schema_migration_exists():
    assert MIGRATION_PATH.exists()


def test_supabase_core_schema_migration_defines_expected_tables_and_policies():
    sql = MIGRATION_PATH.read_text()

    assert "create table if not exists public.profiles" in sql
    assert "create table if not exists public.guardian_links" in sql
    assert "create table if not exists public.devices" in sql
    assert "create table if not exists public.pressure_events" in sql
    assert "create table if not exists public.transfer_events" in sql
    assert "create table if not exists public.risk_assessments" in sql
    assert "create table if not exists public.guardian_notifications" in sql
    assert "alter table public.profiles enable row level security" in sql
    assert "create policy profiles_select_own" in sql
    assert "create policy guardian_notifications_select_related" in sql

# Supabase

Database schema, migrations, and Supabase-related configuration for the CVT Detection Project.

This project uses Supabase for:
- Authentication
- Database
- Event logging
- Guardian notification data
- Risk scoring result storage

## Current Schema

Core migration:
- `supabase/migrations/20260620_create_cvt_core_schema.sql`

Defined tables:
- `profiles`
- `guardian_links`
- `devices`
- `pressure_events`
- `transfer_events`
- `risk_assessments`
- `guardian_notifications`

The migration also includes:
- enum types for roles, risk levels, actions, and notification states
- foreign keys between the core event tables
- indexes for profile/event lookup
- row level security policies for self-owned and related records

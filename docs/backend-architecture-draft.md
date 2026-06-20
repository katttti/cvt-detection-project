# Backend Architecture Draft

## Scope

This draft defines the first backend slice for the CVT Detection Project based on the current repository structure and the provided flow diagrams.

Working assumption:
- Backend stack: Python FastAPI
- Database and auth: Supabase
- Public deployment target: one Mac mini exposing two external endpoints

## Product Flow

1. The mobile app computes an on-device `pressure_score` from message context.
2. When the user reaches a transfer attempt, the app sends transfer metadata plus `pressure_score` to the backend.
3. The backend computes a final `risk_score`.
4. The backend returns a risk level (`yellow`, `orange`, `red`) and the next action.
5. For `red`, the backend also creates a guardian notification event.

## Recommended Public Server Layout

One Mac mini can safely host two externally reachable services:

1. `api` server
   - FastAPI service for risk scoring, event ingestion, and guardian notification triggers
   - Example local port: `8000`

2. `ops` server
   - Lightweight admin or monitoring surface for logs, notification history, and health checks
   - Example local port: `3000`

Recommended exposure method:
- Run both services locally with `pm2`
- Put a reverse proxy or tunnel in front
- Prefer Cloudflare Tunnel for early-stage deployment because it avoids router port forwarding

## Supabase Data Model

### Core tables

#### `profiles`

Application users.

| column | type | notes |
| --- | --- | --- |
| `id` | `uuid` | primary key, linked to Supabase auth user |
| `role` | `text` | `teen`, `guardian`, `admin` |
| `display_name` | `text` | user-facing name |
| `phone` | `text` | optional |
| `created_at` | `timestamptz` | default now |

#### `guardian_links`

Maps teens to guardians.

| column | type | notes |
| --- | --- | --- |
| `id` | `uuid` | primary key |
| `teen_id` | `uuid` | references `profiles.id` |
| `guardian_id` | `uuid` | references `profiles.id` |
| `status` | `text` | `pending`, `active`, `revoked` |
| `created_at` | `timestamptz` | default now |

#### `devices`

Tracks mobile devices that produce on-device scores.

| column | type | notes |
| --- | --- | --- |
| `id` | `uuid` | primary key |
| `profile_id` | `uuid` | references `profiles.id` |
| `device_label` | `text` | optional |
| `platform` | `text` | `ios`, `android` |
| `created_at` | `timestamptz` | default now |

#### `pressure_events`

On-device scoring outputs.

| column | type | notes |
| --- | --- | --- |
| `id` | `uuid` | primary key |
| `profile_id` | `uuid` | references `profiles.id` |
| `device_id` | `uuid` | references `devices.id` |
| `pressure_score` | `numeric` | normalized 0-1 or 0-100 |
| `signal_summary` | `jsonb` | no raw message body |
| `occurred_at` | `timestamptz` | client event time |
| `created_at` | `timestamptz` | default now |

#### `transfer_events`

Transfer attempts sent from the app.

| column | type | notes |
| --- | --- | --- |
| `id` | `uuid` | primary key |
| `profile_id` | `uuid` | references `profiles.id` |
| `amount` | `numeric` | transfer amount |
| `recipient_hash` | `text` | hashed account or recipient identifier |
| `is_new_recipient` | `boolean` | feature input |
| `occurred_at` | `timestamptz` | client event time |
| `created_at` | `timestamptz` | default now |

#### `risk_assessments`

Final backend scoring results.

| column | type | notes |
| --- | --- | --- |
| `id` | `uuid` | primary key |
| `profile_id` | `uuid` | references `profiles.id` |
| `pressure_event_id` | `uuid` | references `pressure_events.id` |
| `transfer_event_id` | `uuid` | references `transfer_events.id` |
| `risk_score` | `numeric` | normalized score |
| `risk_level` | `text` | `yellow`, `orange`, `red` |
| `reason_codes` | `text[]` | explainable rule outputs |
| `recommended_action` | `text` | `allow`, `warn`, `delay`, `notify_guardian` |
| `created_at` | `timestamptz` | default now |

#### `guardian_notifications`

Records guardian alert attempts and delivery state.

| column | type | notes |
| --- | --- | --- |
| `id` | `uuid` | primary key |
| `risk_assessment_id` | `uuid` | references `risk_assessments.id` |
| `guardian_id` | `uuid` | references `profiles.id` |
| `channel` | `text` | `push`, `sms`, `in_app` |
| `delivery_status` | `text` | `queued`, `sent`, `failed`, `read` |
| `sent_at` | `timestamptz` | nullable |
| `created_at` | `timestamptz` | default now |

## Backend API Boundaries

### `POST /v1/pressure-events`

Stores an on-device pressure result.

Request body:
- `profile_id`
- `device_id`
- `pressure_score`
- `signal_summary`
- `occurred_at`

### `POST /v1/transfer-events`

Stores a transfer attempt before risk scoring.

Request body:
- `profile_id`
- `amount`
- `recipient_hash`
- `is_new_recipient`
- `occurred_at`

### `POST /v1/risk-assessments`

Combines the latest pressure event and transfer metadata, then returns a final decision.

Request body:
- `profile_id`
- `pressure_event_id`
- `transfer_event_id`

Response body:
- `risk_score`
- `risk_level`
- `reason_codes`
- `recommended_action`

### `GET /v1/guardian-notifications`

Guardian-facing notification history.

### `GET /health`

Simple health check for public exposure and uptime monitoring.

## Risk Scoring Rules

Initial backend logic should stay simple:

1. Start from `pressure_score`
2. Add weight when recipient is new
3. Add weight for late-night transfer attempts
4. Add weight for unusually large amount
5. Add weight for repeated urgent attempts in a short window

Example action thresholds:
- `yellow`: warning only
- `orange`: stronger confirmation and extra warning
- `red`: guardian notification plus optional transfer delay

## Mac mini Deployment Steps

1. Install runtime tools
   - `brew install python@3.12`
   - `brew install cloudflared`
2. Run backend API on `127.0.0.1:8000`
3. Run ops service on `127.0.0.1:3000`
4. Use `pm2` to keep both services alive
5. Create two public hostnames with Cloudflare Tunnel
   - `api.<your-domain>`
   - `ops.<your-domain>`
6. Add HTTPS and tunnel routing
7. Verify external access from a mobile network, not only from local Wi-Fi

## Immediate Implementation Order

1. Add Supabase SQL schema and migrations
2. Scaffold FastAPI project in `backend/`
3. Implement health check and event ingestion endpoints
4. Implement rule-based `risk_assessment` endpoint
5. Add guardian notification persistence
6. Add PM2 ecosystem config for Mac mini deployment

## Open Decisions

1. Whether the second public server should be an admin dashboard or a guardian-specific API
2. Whether `risk_score` should be stored as `0-1` or `0-100`
3. Whether the first guardian notification should be push-only or include SMS fallback

# Backend

Backend API server for CVT detection.

Current recommended direction:
- Framework: FastAPI
- Database and auth: Supabase
- Deployment target: Mac mini with two externally reachable services

Planned responsibilities:
- Accept on-device `pressure_score` events
- Accept transfer attempt metadata
- Compute backend `risk_score`
- Record guardian notification events
- Expose health and ops endpoints for external monitoring

See [docs/backend-architecture-draft.md](../docs/backend-architecture-draft.md) for the current backend and data model draft.
See [docs/mac-mini-public-server-checklist.md](../docs/mac-mini-public-server-checklist.md) for the deployment checklist to expose two public services from the Mac mini.
See [docs/public-access-runbook.md](../docs/public-access-runbook.md) for temporary sharing vs long-lived public URL setup.

## Current Local Backend

Implemented endpoints:
- `GET /health`
- `POST /v1/pressure-events`
- `POST /v1/transfer-events`
- `POST /v1/risk-assessments`
- `GET /v1/guardian-notifications`

Security:
- API routes under `/v1/*` require `X-Access-Password`
- Ops server uses HTTP Basic auth

## Local Run

Create the virtual environment and install dependencies:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
```

Create the local environment file:

```bash
cp backend/.env.example backend/.env
```

If `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set, the API writes to Supabase.
If they are omitted, the API falls back to the in-memory development store.

Start the API server:

```bash
CVT_SHARED_PASSWORD="replace-me" \
backend/.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 3000
```

Start the ops server:

```bash
CVT_SHARED_PASSWORD="replace-me" \
CVT_OPS_USERNAME="friend" \
backend/.venv/bin/python -m uvicorn backend.app.ops:ops_app --host 0.0.0.0 --port 3001
```

To use the real Supabase schema, install the Python client and pass the service role key:

```bash
backend/.venv/bin/pip install -r backend/requirements.txt

CVT_SHARED_PASSWORD="replace-me" \
SUPABASE_URL="https://your-project.supabase.co" \
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key" \
backend/.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 3000
```

Real Supabase writes require valid upstream records:
- `profiles.id` must already exist for each `profile_id`
- `devices.id` must already exist for each `device_id`
- `guardian_links` should contain active teen-to-guardian mappings if you want `red` risk events to create guardian notifications

Or run both with `pm2` using [ecosystem.config.cjs](./ecosystem.config.cjs).
For repeatable startup on the Mac mini, use:

```bash
chmod +x backend/start_services.sh backend/check_services.sh
backend/start_services.sh
backend/check_services.sh
```

## Router Port Forwarding

If your router already forwards:
- external `10808` -> internal `192.168.0.187:3000`

then the backend API should run on internal port `3000`.

To expose the second public service, add one more forwarding rule:
- external `10809` -> internal `192.168.0.187:3001`

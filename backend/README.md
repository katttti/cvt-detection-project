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

Or run both with `pm2` using [ecosystem.config.cjs](./ecosystem.config.cjs).

## Router Port Forwarding

If your router already forwards:
- external `10808` -> internal `192.168.0.187:3000`

then the backend API should run on internal port `3000`.

To expose the second public service, add one more forwarding rule:
- external `10809` -> internal `192.168.0.187:3001`

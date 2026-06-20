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

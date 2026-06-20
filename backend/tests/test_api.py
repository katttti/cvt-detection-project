import httpx
import pytest

from backend.app.main import app


@pytest.mark.anyio
async def test_health_endpoint_reports_ok():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_risk_assessment_endpoint_returns_red_action_for_high_risk_request():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/risk-assessments",
            headers={"X-Access-Password": "dev-password"},
            json={
                "profile_id": "b98d39e6-6ebd-4511-8bd1-82c4fce01b84",
                "pressure_event_id": "b1afdf5d-e4e9-4d14-8cb1-56b31d9b2a31",
                "transfer_event_id": "87e6d3c1-5993-4a89-bf40-0e9f29053df8",
                "pressure_score": 0.91,
                "amount": 150000,
                "is_new_recipient": True,
                "occurred_at": "2026-06-20T01:13:00+09:00",
                "recent_urgent_attempts": 3,
            },
        )

    body = response.json()

    assert response.status_code == 200
    assert body["risk_level"] == "red"
    assert body["recommended_action"] == "notify_guardian"
    assert "late_night_transfer" in body["reason_codes"]


@pytest.mark.anyio
async def test_risk_assessment_endpoint_rejects_missing_access_password():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/risk-assessments",
            json={
                "profile_id": "b98d39e6-6ebd-4511-8bd1-82c4fce01b84",
                "pressure_event_id": "b1afdf5d-e4e9-4d14-8cb1-56b31d9b2a31",
                "transfer_event_id": "87e6d3c1-5993-4a89-bf40-0e9f29053df8",
                "pressure_score": 0.91,
                "amount": 150000,
                "is_new_recipient": True,
                "occurred_at": "2026-06-20T01:13:00+09:00",
                "recent_urgent_attempts": 3,
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access password"

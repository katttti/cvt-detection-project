import httpx
import pytest

from backend.app.main import app
from backend.app.store import get_store


@pytest.fixture(autouse=True)
def reset_store_cache():
    get_store.cache_clear()
    yield
    get_store.cache_clear()


@pytest.mark.anyio
async def test_red_risk_assessment_creates_guardian_notification_linked_to_assessment():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        assessment_response = await client.post(
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
        notifications_response = await client.get(
            "/v1/guardian-notifications",
            headers={"X-Access-Password": "dev-password"},
        )

    assessment_body = assessment_response.json()
    notifications_body = notifications_response.json()

    assert assessment_response.status_code == 200
    assert "id" in assessment_body
    assert notifications_response.status_code == 200
    assert notifications_body[0]["guardian_id"] == assessment_body["profile_id"]
    assert notifications_body[0]["risk_assessment_id"] == assessment_body["id"]

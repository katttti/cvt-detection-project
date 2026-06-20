import base64

import httpx
import pytest

from backend.app.ops import ops_app


def _basic_auth_header(username: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.mark.anyio
async def test_ops_root_requires_basic_auth():
    transport = httpx.ASGITransport(app=ops_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_ops_root_returns_service_summary_when_authenticated():
    transport = httpx.ASGITransport(app=ops_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/", headers=_basic_auth_header("friend", "dev-password"))

    body = response.json()

    assert response.status_code == 200
    assert body["service"] == "cvt-ops"
    assert body["api_port"] == 8000
    assert body["ops_port"] == 3000

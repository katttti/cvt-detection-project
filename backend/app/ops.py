from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasicCredentials

from backend.app.auth import ops_basic, verify_ops_credentials

ops_app = FastAPI(title="CVT Ops Server", version="0.1.0")


@ops_app.get("/")
def ops_root(credentials: HTTPBasicCredentials = Depends(ops_basic)) -> dict[str, object]:
    verify_ops_credentials(credentials)
    return {
        "service": "cvt-ops",
        "status": "ok",
        "api_port": 3000,
        "ops_port": 3001,
        "public_routes": ["/", "/healthz"],
    }


@ops_app.get("/healthz")
def ops_health() -> dict[str, str]:
    return {"status": "ok"}

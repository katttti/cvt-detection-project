import os
import secrets

from fastapi import Header, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


ACCESS_PASSWORD = os.getenv("CVT_SHARED_PASSWORD", "dev-password")
OPS_USERNAME = os.getenv("CVT_OPS_USERNAME", "friend")

ops_basic = HTTPBasic()


def verify_access_password(x_access_password: str | None = Header(default=None)) -> None:
    if not x_access_password or not secrets.compare_digest(x_access_password, ACCESS_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access password",
        )


def verify_ops_credentials(credentials: HTTPBasicCredentials) -> None:
    username_ok = secrets.compare_digest(credentials.username, OPS_USERNAME)
    password_ok = secrets.compare_digest(credentials.password, ACCESS_PASSWORD)
    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ops credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

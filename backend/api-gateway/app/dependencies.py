from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_token
from app.config import settings
from app.database import SessionLocal


def get_settings():
    return settings


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for each request.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> dict:
    """
    Validate the access token and return its payload.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = decode_token(token)

        if not payload:
            raise credentials_exception

        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")
        role = payload.get("role")
        tenant_id = payload.get("tenant_id")

        if not user_id:
            raise credentials_exception

        if not role:
            raise credentials_exception

        if not tenant_id:
            raise credentials_exception

        return payload

    except HTTPException:
        raise

    except Exception:
        raise credentials_exception


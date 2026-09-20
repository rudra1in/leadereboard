import uuid

from sqlalchemy.orm import Session

from app.auth.models import User, UserRole
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)


def register_user(
    db: Session,
    email: str,
    password: str,
    role: UserRole,
    tenant_id: str,
) -> User:

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise ValueError("User already exists")

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password_hash=hash_password(password),
        role=role.value,
        tenant_id=tenant_id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_tokens(user: User) -> dict:

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=user.tenant_id,
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
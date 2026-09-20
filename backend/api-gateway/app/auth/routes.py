from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.service import (
    authenticate_user,
    create_tokens,
    register_user,
)
from app.dependencies import get_db


router = APIRouter(
    prefix="/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(
            db=db,
            email=request.email,
            password=request.password,
            role=request.role,
            tenant_id=request.tenant_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return create_tokens(user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return create_tokens(user)
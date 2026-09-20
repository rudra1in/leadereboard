from fastapi import APIRouter, Depends

from app.dependencies import get_current_user


router = APIRouter(
    prefix="/v1/users",
    tags=["Users"],
)


@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    return {
        "user_id": current_user["sub"],
        "role": current_user["role"],
        "tenant_id": current_user["tenant_id"],
    }
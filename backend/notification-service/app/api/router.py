from fastapi import APIRouter

from app.api.routers import notifications

router = APIRouter()

router.include_router(notifications.router)
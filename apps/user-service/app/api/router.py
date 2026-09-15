from fastapi import APIRouter
from app.api.routes import users, sse

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(sse.router)

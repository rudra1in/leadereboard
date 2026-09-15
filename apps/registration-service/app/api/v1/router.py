"""API v1 router - aggregates all route groups."""

from fastapi import APIRouter

from app.api.v1.routes import registrations, sse


api_router = APIRouter()

# Include route groups
api_router.include_router(registrations.router)
api_router.include_router(sse.router)

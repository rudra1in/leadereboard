import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.schedule import Schedule
from app.services.conflict_detector import check_conflict


router = APIRouter(
    prefix="/v1/schedules",
    tags=["Scheduling"]
)


class ScheduleCreate(BaseModel):
    event_id: uuid.UUID
    match_id: uuid.UUID
    court_id: uuid.UUID
    referee_id: uuid.UUID
    start_time: datetime
    end_time: datetime


class ScheduleUpdate(BaseModel):
    court_id: uuid.UUID | None = None
    referee_id: uuid.UUID | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None
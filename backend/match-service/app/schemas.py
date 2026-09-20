from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    READY = "READY"
    LIVE = "LIVE"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"


class MatchCreate(BaseModel):
    event_id: int
    sport: str
    venue_id: int
    court_id: int | None = None
    participant_a_id: int
    participant_b_id: int
    scheduled_at: datetime


class MatchUpdate(BaseModel):
    venue_id: int | None = None
    court_id: int | None = None
    scheduled_at: datetime | None = None


class MatchResponse(BaseModel):
    id: int
    event_id: int
    sport: str
    venue_id: int
    court_id: int | None
    participant_a_id: int
    participant_b_id: int
    scheduled_at: datetime
    status: MatchStatus

    class Config:
        from_attributes = True
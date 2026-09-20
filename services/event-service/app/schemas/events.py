from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    name: str
    sport: str
    description: str | None = None
    start_date: datetime
    end_date: datetime
    venue_id: UUID | None = None
    status: str = "DRAFT"
    capacity: int | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: str | None = None
    sport: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    venue_id: UUID | None = None
    status: str | None = None
    capacity: int | None = None


class EventResponse(EventBase):
    id: UUID
    tenant_id: UUID

    model_config = ConfigDict(
        from_attributes=True
    )
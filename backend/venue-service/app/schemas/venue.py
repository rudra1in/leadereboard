from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VenueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None

    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str | None = None
    country: str = Field(..., min_length=1, max_length=100)

    capacity: int | None = Field(
        default=None,
        ge=1,
    )


class VenueUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    address: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    city: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    state: str | None = None

    country: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    capacity: int | None = Field(
        default=None,
        ge=1,
    )

    is_active: bool | None = None


class VenueResponse(BaseModel):
    id: UUID
    tenant_id: UUID

    name: str
    description: str | None

    address: str
    city: str
    state: str | None
    country: str

    capacity: int | None
    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
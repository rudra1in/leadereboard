from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    sport: str
    nationality: Optional[str] = None
    profile_image_url: Optional[str] = None


class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    sport: Optional[str] = None
    nationality: Optional[str] = None
    profile_image_url: Optional[str] = None


class AthleteResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    first_name: str
    last_name: str
    date_of_birth: Optional[str]
    gender: Optional[str]
    sport: str
    nationality: Optional[str]
    profile_image_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)
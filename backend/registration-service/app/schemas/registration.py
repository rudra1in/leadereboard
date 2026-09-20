from pydantic import BaseModel, EmailStr
from datetime import datetime

class RegistrationCreate(BaseModel):
    event_id: int
    full_name: str
    email: EmailStr
    phone: str | None = None

class RegistrationRead(BaseModel):
    id: int
    event_id: int
    full_name: str
    email: str
    phone: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
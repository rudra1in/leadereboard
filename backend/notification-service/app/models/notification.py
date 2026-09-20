from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"


class NotificationRequest(BaseModel):
    recipient: str = Field(..., min_length=1)
    subject: str | None = None
    message: str = Field(..., min_length=1)
    notification_type: NotificationType
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    notification_id: str
    status: str
    notification_type: NotificationType
from fastapi import APIRouter

from app.models.notification import (
    NotificationRequest,
    NotificationResponse,
)
from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/v1/notifications",
    tags=["Notifications"],
)


notification_service = NotificationService()


@router.post(
    "/",
    response_model=NotificationResponse,
)
def create_notification(
    notification: NotificationRequest,
):
    return notification_service.send_notification(notification)
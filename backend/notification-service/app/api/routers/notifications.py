from fastapi import APIRouter,status

from app.models.notification import (
    NotificationRequest,
    NotificationResponse,
)
from app.services.notification_service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


notification_service = NotificationService()


@router.post("/",response_model=NotificationResponse,status_code=status.HTTP_202_ACCEPTED)
def create_notification(notification: NotificationRequest):
    return notification_service.send_notification(notification)
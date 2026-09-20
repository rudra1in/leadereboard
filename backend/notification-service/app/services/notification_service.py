import uuid

from app.models.notification import (
    NotificationRequest,
    NotificationResponse,
)


class NotificationService:

    def send_notification(
        self,
        notification: NotificationRequest,
    ) -> NotificationResponse:

        notification_id = str(uuid.uuid4())

        print(
            f"[NOTIFICATION] "
            f"type={notification.notification_type.value} "
            f"recipient={notification.recipient} "
            f"message={notification.message}"
        )

        return NotificationResponse(
            notification_id=notification_id,
            status="accepted",
            notification_type=notification.notification_type,
        )
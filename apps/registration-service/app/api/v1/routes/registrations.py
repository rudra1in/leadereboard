from fastapi import APIRouter, status
from uuid import uuid4
from app.schemas.registration import RegistrationCreate
from app.core.kafka_producer  import kafka_producer
from app.core.config import settings

router = APIRouter(prefix="/registrations", tags=["registrations"])

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_registration(payload: RegistrationCreate):
    registration_id = str(uuid4())

    message = {
        "registration_id": registration_id,
        "event_id": payload.event_id,
        "full_name": payload.full_name,
        "email": payload.email,
        "phone": payload.phone,
    }

    await kafka_producer.send(settings.KAFKA_TOPIC_REGISTRATIONS, message)

    return {
        "message": "Registration submitted successfully",
        "registration_id": registration_id,
        "status": "processing"
    }
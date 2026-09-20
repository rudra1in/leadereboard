"""Registration creation endpoint.

Writes to the database and publishes to Kafka in the same request,
then returns the final result — no async "processing" round trip needed.
"""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.registration import RegistrationCreate, RegistrationRead
from app.core.kafka_producer import kafka_producer
from app.core.config import settings
from app.core.database import get_db
from app.models.registration import Registration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.post("", response_model=RegistrationRead, status_code=status.HTTP_201_CREATED)
async def create_registration(
    payload: RegistrationCreate,
    db: AsyncSession = Depends(get_db),
):
    # 1. Write to the database first — this is the durable source of truth.
    registration = Registration(
        event_id=payload.event_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        status="confirmed",
    )
    try:
       db.add(registration)
    except Exception as e:
            # DB write already succeeded — don't fail the request over Kafka.
            # Log loudly so it can be replayed/reconciled.
            logger.error(f"Registration {registration.id} not saved")
   
    await db.flush()          # get_db() commits on successful return / rolls back on exception
    await db.refresh(registration)

    # 2. Publish the event to Kafka in the same request, now that we know it's saved.
    message = {
        "registration_id": registration.id,
        "event_id": registration.event_id,
        "full_name": registration.full_name,
        "email": registration.email,
        "phone": registration.phone,
        "status": registration.status,
    }
    try:
        await kafka_producer.send(settings.KAFKA_TOPIC_REGISTRATIONS, message)
    except Exception as e:
        # DB write already succeeded — don't fail the request over Kafka.
        # Log loudly so it can be replayed/reconciled.
        logger.error(f"Registration {registration.id} saved but Kafka publish failed: {e}")

    # 3. Return the real, final result.
    return registration
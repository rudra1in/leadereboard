import asyncio
import json
import logging

import httpx
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.registration import Registration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_registration():
    logger.info("Starting Registration Processor...")
    logger.info(f"Connecting to Kafka: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    logger.info(f"Consuming topic: {settings.KAFKA_TOPIC_REGISTRATIONS}")

    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_REGISTRATIONS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="registration-processor",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    await consumer.start()
    await producer.start()
    logger.info("Kafka Consumer and Producer started successfully")

    try:
        async for msg in consumer:
            data = msg.value
            logger.info(f"Received message: {data}")

            try:
                async with AsyncSessionLocal() as session:
                    # 1. Save to DB
                    registration = Registration(
                        event_id=data["event_id"],
                        full_name=data["full_name"],
                        email=data["email"],
                        phone=data.get("phone"),
                        status="confirmed",
                    )
                    session.add(registration)
                    await session.commit()
                    await session.refresh(registration)

                    result = {
                        "registration_id": data["registration_id"],
                        "db_id": registration.id,
                        "status": "confirmed",
                        "full_name": registration.full_name,
                        "email": registration.email,
                        "message": "Registration confirmed successfully!",
                    }

                    # 2. Call Notification Service (through Linkerd mesh)
                    try:
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            notify_payload = {
                                "registration_id": data["registration_id"],
                                "email": registration.email,
                                "full_name": registration.full_name,
                                "message": (
                                    f"Welcome {registration.full_name}! "
                                    "Your registration is confirmed."
                                ),
                            }
                            resp = await client.post(
                                settings.NOTIFICATION_SERVICE_URL,
                                json=notify_payload,
                            )
                            resp.raise_for_status()
                            logger.info(f"Notification service response: {resp.json()}")
                    except Exception as e:
                        # Do not fail the registration if notification fails.
                        # Linkerd can still retry the call if configured.
                        logger.error(
                            f"Notification call failed: {e}",
                            exc_info=True,
                        )

                    # 3. Publish result to Kafka (existing behaviour)
                    logger.info("=" * 50)
                    logger.info(f"Preparing to send result to topic: {settings.KAFKA_TOPIC_RESULTS}")
                    logger.info(f"Result payload: {result}")

                    try:
                        await producer.send_and_wait(
                            settings.KAFKA_TOPIC_RESULTS, result
                        )
                        logger.info(
                            f"SUCCESS: Result published to {settings.KAFKA_TOPIC_RESULTS}"
                        )
                        logger.info(f"registration_id: {data['registration_id']}")
                    except Exception as e:
                        logger.error(f"FAILED to publish result: {e}", exc_info=True)

                    logger.info("=" * 50)

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

    finally:
        await consumer.stop()
        await producer.stop()
        logger.info("Consumer stopped")


if __name__ == "__main__":
    asyncio.run(process_registration())
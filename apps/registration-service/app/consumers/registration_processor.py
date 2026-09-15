import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.registration import Registration
from app.core.config import settings

async def process_registration():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_REGISTRATIONS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="registration-processor",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    await consumer.start()
    await producer.start()

    try:
        async for msg in consumer:
            data = msg.value
            print(f"Processing registration: {data['registration_id']}")

            async with AsyncSessionLocal() as session:
                registration = Registration(
                    event_id=data["event_id"],
                    full_name=data["full_name"],
                    email=data["email"],
                    phone=data.get("phone"),
                    status="confirmed"
                )
                session.add(registration)
                await session.commit()
                await session.refresh(registration)

                # Publish result
                result = {
                    "registration_id": data["registration_id"],
                    "db_id": registration.id,
                    "status": "confirmed",
                    "full_name": registration.full_name,
                    "email": registration.email,
                    "message": "Registration confirmed successfully!"
                }
                await producer.send_and_wait(settings.KAFKA_TOPIC_RESULTS, result)
                print(f"Result published for {data['registration_id']}")

    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(process_registration())
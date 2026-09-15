import asyncio
import json
from aiokafka import AIOKafkaConsumer
from app.core.config import settings

# In-memory store of connected SSE clients (for demo)
# In production use Redis Pub/Sub
sse_clients = {}

async def broadcast_results():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_RESULTS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="sse-broadcaster",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()

    try:
        async for msg in consumer:
            data = msg.value
            registration_id = data["registration_id"]
            print(f"Broadcasting result for {registration_id}")

            # Send to specific client if connected
            if registration_id in sse_clients:
                queue = sse_clients[registration_id]
                await queue.put(data)

    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(broadcast_results())
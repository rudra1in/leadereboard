# app/core/kafka_broadcaster.py  (or wherever it is)

import asyncio
import json
import logging
from kafka_template.template import KafkaTemplate
#from company_common_kafka.dependencies import KafkaTemplateDep
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.core.sse import sse_clients   # ← shared dictionary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_sse_broadcaster():          # ← renamed
    logger.info(">>> Starting SSE Broadcaster inside FastAPI...")
    logger.info(f"Kafka: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    logger.info(f"Listening to topic: {settings.KAFKA_TOPIC_RESULTS}")

    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_RESULTS,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="sse-broadcaster-fastapi",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    await consumer.start()
    logger.info(">>> SSE Broadcaster successfully connected to Kafka")

    try:
        async for msg in consumer:
            data = msg.value
            registration_id = data.get("registration_id")

            if not registration_id:
                logger.warning(f"Received message without registration_id: {data}")
                continue

            logger.info(f"Broadcasting result for {registration_id} → {data.get('status')}")

            if registration_id in sse_clients:
                await sse_clients[registration_id].put(data)
                logger.info(f"Message delivered to SSE client: {registration_id}")
            else:
                logger.warning(f"No active SSE client for registration_id: {registration_id}")

    except Exception as e:
        logger.error(f"Error in broadcaster: {e}", exc_info=True)
    finally:
        await consumer.stop()
        logger.info("SSE Broadcaster stopped")
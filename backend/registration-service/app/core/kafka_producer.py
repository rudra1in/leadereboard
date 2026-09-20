# import json
# import logging
# #from aiokafka import AIOKafkaProducer
# import asyncio
# from confluent_kafka.aio import AIOProducer

# from app.core.config import settings

# logger = logging.getLogger(__name__)

# class KafkaProducer:
#     def __init__(self):
#         self.producer: AIOKafkaProducer | None = None

#     async def start(self):
#         self.producer = AIOKafkaProducer(
#             bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
#             value_serializer=lambda v: json.dumps(v).encode("utf-8"),
#         )
#         await self.producer.start()
#         logger.info("Kafka producer started")

#     async def stop(self):
#         if self.producer:
#             await self.producer.stop()

#     async def send(self, topic: str, message: dict):
#         if not self.producer:
#             raise RuntimeError("Producer not started")
#         await self.producer.send_and_wait(topic, message)
#         logger.info(f"Sent to {topic}: {message}")

# kafka_producer = KafkaProducer()
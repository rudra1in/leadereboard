import json
import logging
from typing import Any, Optional, Union

from confluent_kafka.aio import AIOProducer
from confluent_kafka import KafkaException

from .config import KafkaSettings
from .interfaces import KafkaProducerInterface

logger = logging.getLogger(__name__)


class KafkaTemplate(KafkaProducerInterface):
    """
    High-performance KafkaTemplate for confluent-kafka 2.15+
    Fully async using the native AIOProducer.
    """

    def __init__(self, settings: KafkaSettings):
        self._settings = settings
        self._producer: Optional[AIOProducer] = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            return

        conf = self._settings.to_confluent_config()
        # AIOProducer is fully async in 2.15
        self._producer = AIOProducer(conf)
        self._started = True

        logger.info(
            "KafkaTemplate started | client_id=%s | brokers=%s",
            self._settings.client_id,
            self._settings.bootstrap_servers,
        )

    async def stop(self) -> None:
        if not self._producer or not self._started:
            return

        try:
            # Critical: flush remaining messages first
            await self._producer.flush()
            await self._producer.close()
        except Exception as e:
            logger.exception("Error while stopping KafkaTemplate: %s", e)
        finally:
            self._producer = None
            self._started = False
            logger.info("KafkaTemplate stopped")

    async def send(
        self,
        topic: str,
        value: Any,
        key: Optional[Union[str, bytes]] = None,
        headers: Optional[list[tuple[str, bytes]]] = None,
        partition: Optional[int] = None,
    ) -> None:
        """Send and wait for delivery confirmation."""
        if not self._started or not self._producer:
            raise RuntimeError("KafkaTemplate is not started")

        value_bytes = self._serialize(value)
        key_bytes = key.encode("utf-8") if isinstance(key, str) else key

        try:
            # In 2.15: produce() returns a Future after awaiting the coroutine
            delivery_future = await self._producer.produce(
                topic=topic,
                value=value_bytes,
                key=key_bytes,
                headers=headers,          # Note: headers support may be limited in batched mode
                partition=partition,
            )
            msg = await delivery_future

            if msg.error():
                raise KafkaException(msg.error())

            logger.debug(
                "Message delivered | topic=%s partition=%s offset=%s",
                msg.topic(), msg.partition(), msg.offset()
            )
        except KafkaException as e:
            logger.exception("Failed to produce message to topic %s", topic)
            raise

    async def send_async(
        self,
        topic: str,
        value: Any,
        key: Optional[Union[str, bytes]] = None,
    ):
        """Fire-and-forget (returns the delivery Future)."""
        if not self._started or not self._producer:
            raise RuntimeError("KafkaTemplate is not started")

        value_bytes = self._serialize(value)
        key_bytes = key.encode("utf-8") if isinstance(key, str) else key

        return await self._producer.produce(
            topic=topic,
            value=value_bytes,
            key=key_bytes,
        )

    def _serialize(self, value: Any) -> bytes:
        if isinstance(value, (bytes, bytearray)):
            return value
        return json.dumps(value, default=str).encode("utf-8")

    @property
    def is_started(self) -> bool:
        return self._started

    @property
    def producer(self) -> AIOProducer:
        if not self._producer:
            raise RuntimeError("KafkaTemplate is not started")
        return self._producer
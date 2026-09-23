
from logging import (
     getLogger,
     logging,
     logger,)


from .config import KafkaSettings
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
)


def kafka_retry():
    """Retry decorator for Kafka publishes. No circuit breaker here on
    purpose - the aiokafka producer already buffers/retries internally
    (retry_backoff_ms), so a breaker would mostly duplicate that. This adds
    a bounded, logged retry on top for the cases that still surface."""
    return retry(
        reraise=True,
        stop=stop_after_attempt(KafkaSettings.KAFKA_RETRY_ATTEMPTS),
        wait=wait_exponential_jitter(
            initial=KafkaSettings.KAFKA_RETRY_BACKOFF_SECONDS, max=3
        ),
        retry=retry_if_exception(_is_transient_kafka_error),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )

def _is_transient_kafka_error(exc: BaseException) -> bool:
    # Broad on purpose: aiokafka raises a family of KafkaError subclasses for
    # broker-unavailable / leader-not-available / request-timed-out style
    # failures, all of which are worth a bounded retry.
    from aiokafka.errors import KafkaError

    return isinstance(exc, KafkaError)


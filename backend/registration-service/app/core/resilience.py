"""Shared resilience building blocks: circuit breaker + timeout + retry.

Applied to the two outbound calls this service makes that can fail
independently of its own health:

  - the gRPC call to the dummy notification-api  (see grpc_client/)
  - publishing to Kafka                          (see kafka_producer.py)

Pattern for each call site: circuit_breaker( retryable( call_with_timeout ) )
  - timeout    caps how long a single attempt can hang
  - retry      re-attempts a bounded number of times on *transient* failures
               only, with exponential backoff + jitter
  - circuit    once a dependency is failing consistently, stop hammering it -
    breaker    fail fast for `reset_timeout` seconds, then allow one probe
               through (half-open) before fully closing again
"""

import logging
from datetime import timedelta

import grpc
from aiobreaker import CircuitBreaker, CircuitBreakerError
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
)

from app.core.config import settings

logger = logging.getLogger("app.resilience")

# ---------------------------------------------------------------------------
# Circuit breakers - one per external dependency, so a slow/broken gRPC
# notification-api doesn't get lumped in with unrelated Kafka issues.
# ---------------------------------------------------------------------------

notification_breaker = CircuitBreaker(
    fail_max=settings.NOTIFICATION_BREAKER_FAIL_MAX,
    timeout_duration=timedelta(seconds=settings.NOTIFICATION_BREAKER_RESET_SECONDS),
    name="notification-grpc-api",
)

# Re-exported so callers can catch it without importing aiobreaker directly.
BreakerOpenError = CircuitBreakerError


def _is_transient_grpc_error(exc: BaseException) -> bool:
    """Only retry errors that are plausibly transient. A caller-side bug
    (INVALID_ARGUMENT) or an explicit application rejection should not be
    retried - retrying those just adds latency for a result that will never
    change."""
    if not isinstance(exc, grpc.aio.AioRpcError):
        return False
    return exc.code() in (
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.DEADLINE_EXCEEDED,
        grpc.StatusCode.RESOURCE_EXHAUSTED,
        grpc.StatusCode.ABORTED,
    )


def grpc_retry():
    """Retry decorator for gRPC calls: bounded attempts, exponential
    backoff with jitter, transient errors only."""
    return retry(
        reraise=True,
        stop=stop_after_attempt(settings.NOTIFICATION_RETRY_ATTEMPTS),
        wait=wait_exponential_jitter(
            initial=settings.NOTIFICATION_RETRY_BACKOFF_SECONDS, max=5
        ),
        retry=retry_if_exception(_is_transient_grpc_error),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )


def _is_transient_kafka_error(exc: BaseException) -> bool:
    # Broad on purpose: aiokafka raises a family of KafkaError subclasses for
    # broker-unavailable / leader-not-available / request-timed-out style
    # failures, all of which are worth a bounded retry.
    from aiokafka.errors import KafkaError

    return isinstance(exc, KafkaError)


def kafka_retry():
    """Retry decorator for Kafka publishes. No circuit breaker here on
    purpose - the aiokafka producer already buffers/retries internally
    (retry_backoff_ms), so a breaker would mostly duplicate that. This adds
    a bounded, logged retry on top for the cases that still surface."""
    return retry(
        reraise=True,
        stop=stop_after_attempt(settings.KAFKA_RETRY_ATTEMPTS),
        wait=wait_exponential_jitter(
            initial=settings.KAFKA_RETRY_BACKOFF_SECONDS, max=3
        ),
        retry=retry_if_exception(_is_transient_kafka_error),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )

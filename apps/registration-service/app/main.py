"""FastAPI application for registration service."""

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.kafka_producer import kafka_producer
from app.core.kafka_broadcaster import start_sse_broadcaster   # ← Add this
from app.api.router import api_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown.
    """
    logger.info("Application starting up...")

    # ========== STARTUP ==========
    try:
        # 1. Start Kafka Producer
        await kafka_producer.start()
        logger.info("Kafka producer started")

        # 2. Start SSE Broadcaster as background task
        broadcaster_task = asyncio.create_task(start_sse_broadcaster())
        logger.info("SSE Broadcaster task created")

    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        raise

    yield  # Application runs here

    # ========== SHUTDOWN ==========
    logger.info("Application shutting down...")

    try:
        # Cancel the broadcaster
        broadcaster_task.cancel()
        try:
            await broadcaster_task
        except asyncio.CancelledError:
            logger.info("SSE Broadcaster stopped")

        # Stop Kafka producer
        await kafka_producer.stop()
        logger.info("Kafka producer stopped")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Event Registration Service with Kafka & SSE",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": "registration-service",
        "version": "0.1.0",
    }


@app.get("/", tags=["root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "api": "/api/v1",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }
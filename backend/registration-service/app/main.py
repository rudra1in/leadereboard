"""FastAPI application for registration service."""

import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from kafka_template.template import KafkaTemplate
from kafka_template.dependencies import KafkaTemplateDep
#from app.core.kafka_producer import kafka_producer
from kafka_template.config import KafkaSettings
from kafka_template.template import KafkaTemplate
from kafka_template.factory import KafkaTemplateFactory
from kafka_template.dependencies import KafkaTemplateDep
from app.api.router import api_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     settings = KafkaSettings()          # reads KAFKA_* environment variables
#     kafka = KafkaTemplate(settings)

#     await kafka.start()
#     app.state.kafka_template = kafka

#     yield

#     await kafka.stop()


# app = FastAPI(lifespan=lifespan)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown.
    """
    logger.info("Application starting up...")

    # ========== STARTUP ==========
    try:
        # 1. Start Kafka Producer
        #await kafka_producer.start()
        logger.info("Kafka producer started")
        settings = KafkaSettings()          # reads KAFKA_* environment variables


        # 2. Start SSE Broadcaster as background task
        broadcaster_task = asyncio.create_task(start_sse_broadcaster())
        logger.info("SSE Broadcaster task created")
        # 3. Start Registration Processor (consumes event.registrations) as background task
        processor_task = asyncio.create_task(process_registration())
        logger.info("Registration Processor task created")

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
        #await kafka_producer.stop()
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
app.include_router(api_router, prefix="/api")


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
            "api": "/api",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }
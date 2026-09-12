"""
GameX Leaderboard Microservice - Main Application

FastAPI application serving the GameX leaderboard rankings API.
Implements microservice architecture with proper OOP patterns.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from database import initialize_database, get_database, close_database
from routers.ranking_router import create_ranking_routers


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

class AppConfig:
    """Application configuration"""
    
    # Basic info
    APP_NAME = "GameX Leaderboard"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "GameX Rankings, Leaderboards & Qualification Microservice"
    
    # API
    API_PREFIX = "/api"
    API_V1_PREFIX = "/api/v1"
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["*"]
    
    # Features
    ENABLE_DOCS = os.getenv("ENABLE_DOCS", "true").lower() == "true"
    ENABLE_REDOC = os.getenv("ENABLE_REDOC", "true").lower() == "true"
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan (startup and shutdown).
    
    This is called when the application starts and stops.
    """
    # Startup
    logger.info(f"Starting {AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")
    
    try:
        initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    try:
        close_database()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    
    # Create app
    app = FastAPI(
        title=AppConfig.APP_NAME,
        description=AppConfig.APP_DESCRIPTION,
        version=AppConfig.APP_VERSION,
        docs_url="/docs" if AppConfig.ENABLE_DOCS else None,
        redoc_url="/redoc" if AppConfig.ENABLE_REDOC else None,
        openapi_url="/openapi.json" if AppConfig.ENABLE_DOCS else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=AppConfig.CORS_ORIGINS,
        allow_credentials=AppConfig.CORS_CREDENTIALS,
        allow_methods=AppConfig.CORS_METHODS,
        allow_headers=AppConfig.CORS_HEADERS,
    )
    
    # Add compression
    app.add_middleware(GZIPMiddleware, minimum_size=1000)
    
    # Register routes
    _register_routes(app)
    
    # Register exception handlers
    _register_exception_handlers(app)
    
    return app


# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

def _register_routes(app: FastAPI):
    """Register all application routes"""
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        db = get_database()
        health = db.health_check()
        
        return {
            "status": "healthy" if health else "unhealthy",
            "service": AppConfig.APP_NAME,
            "version": AppConfig.APP_VERSION,
            "environment": AppConfig.ENVIRONMENT
        }
    
    # Readiness check endpoint
    @app.get("/ready")
    async def readiness_check():
        """Readiness check endpoint"""
        db = get_database()
        ready = db.health_check()
        
        if not ready:
            return JSONResponse(
                status_code=503,
                content={"status": "not-ready", "reason": "Database unavailable"}
            )
        
        return {"status": "ready"}
    
    # Register ranking routers
    ranking_router, admin_router = create_ranking_routers()
    
    app.include_router(ranking_router)
    app.include_router(admin_router)
    
    logger.info("Routes registered successfully")


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

def _register_exception_handlers(app: FastAPI):
    """Register exception handlers"""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """Handle validation errors"""
        logger.error(f"Validation error on {request.url}: {str(exc)}")
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "detail": str(exc),
                "status_code": 422
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception on {request.url}: {str(exc)}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "status_code": 500
            }
        )


# ============================================================================
# APPLICATION INSTANCE
# ============================================================================

app = create_app()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=AppConfig.DEBUG,
        log_level="info"
    )

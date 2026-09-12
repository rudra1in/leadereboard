"""
Database configuration and session management.

Provides SQLAlchemy engine and session factory for database operations.
Implements dependency injection for database sessions in routers.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

from models.ranking_model import Base


logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration settings"""
    
    # Database URL
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://gamex:gamex_password@localhost:5432/gamex_leaderboard"
    )
    
    # Connection pool settings
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
    
    # Logging
    ECHO_SQL = os.getenv("DB_ECHO_SQL", "false").lower() == "true"
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_engine_kwargs(cls) -> dict:
        """Get SQLAlchemy engine keyword arguments"""
        return {
            "echo": cls.ECHO_SQL,
            "poolclass": QueuePool,
            "pool_size": cls.POOL_SIZE,
            "max_overflow": cls.MAX_OVERFLOW,
            "pool_recycle": cls.POOL_RECYCLE,
            "pool_pre_ping": cls.POOL_PRE_PING,
        }


class Database:
    """Database manager"""
    
    def __init__(self):
        """Initialize database"""
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """Initialize database connection and create tables"""
        if self._initialized:
            return
        
        try:
            # Create engine
            self.engine = create_engine(
                DatabaseConfig.get_database_url(),
                **DatabaseConfig.get_engine_kwargs()
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Add event listeners
            self._configure_listeners()
            
            logger.info("Database initialized successfully")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def _configure_listeners(self):
        """Configure SQLAlchemy event listeners"""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Configure connection on creation"""
            if "postgresql" in DatabaseConfig.DATABASE_URL:
                # Enable connection pooling for PostgreSQL
                dbapi_connection.autocommit = False
        
        @event.listens_for(self.engine, "pool_checkout")
        def receive_pool_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log pool checkout for monitoring"""
            pass  # Can add logging here if needed
    
    def get_session(self) -> Session:
        """Get new database session"""
        if not self._initialized:
            self.initialize()
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def health_check(self) -> bool:
        """Check database health"""
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database instance
_db = Database()


def initialize_database():
    """Initialize database at application startup"""
    _db.initialize()


def get_database() -> Database:
    """Get database instance"""
    return _db


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Used in FastAPI route handlers:
    
    @app.get("/rankings")
    async def get_rankings(db: Session = Depends(get_db)):
        # db is automatically injected
    """
    db = _db.get_session()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def close_database():
    """Close database at application shutdown"""
    _db.close()


# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def create_all_tables():
    """Create all database tables"""
    _db.initialize()
    logger.info("All tables created successfully")


def drop_all_tables():
    """Drop all database tables (for testing/development)"""
    if not _db.engine:
        _db.initialize()
    
    Base.metadata.drop_all(bind=_db.engine)
    logger.warning("All tables dropped!")


def reset_database():
    """Reset database (drop and recreate all tables)"""
    drop_all_tables()
    create_all_tables()
    logger.info("Database reset completed")


def migrate_to_schema():
    """Run migrations (placeholder for Alembic integration)"""
    # TODO: Integrate with Alembic for production migrations
    create_all_tables()


if __name__ == "__main__":
    # Initialize when run as script
    initialize_database()
    print("Database initialized successfully!")

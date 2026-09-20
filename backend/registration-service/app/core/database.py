"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=getattr(settings, "DEBUG", False),
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 1. Define Base FIRST
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass

# 2. Import models AFTER Base is created so they attach to Base.metadata
from app.models.registration import Registration

async def init_db():
    print("Tables discovered by SQLAlchemy:", list(Base.metadata.tables.keys()))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency for database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
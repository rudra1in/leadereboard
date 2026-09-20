from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================================
# PostgreSQL Configuration
# ============================================================

DATABASE_URL = "postgresql://gamex:rudra_1978@127.0.0.1:5432/gamex"

# ============================================================
# SQLAlchemy Engine
# ============================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ============================================================
# Database Session Factory
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# Base Class for SQLAlchemy Models
# ============================================================

Base = declarative_base()


# ============================================================
# FastAPI Database Dependency
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
import uuid

from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    sport = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    start_date = Column(
        DateTime,
        nullable=False
    )

    end_date = Column(
        DateTime,
        nullable=False
    )

    venue_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="DRAFT"
    )

    capacity = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
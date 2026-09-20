import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Venue(Base):
    __tablename__ = "venues"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    address = Column(
        String(500),
        nullable=False,
    )

    city = Column(
        String(100),
        nullable=False,
    )

    state = Column(
        String(100),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=False,
    )

    capacity = Column(
        Integer,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    event_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    match_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    court_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    referee_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    start_time = Column(
        DateTime,
        nullable=False
    )

    end_time = Column(
        DateTime,
        nullable=False
    )

    status = Column(
        String(50),
        default="SCHEDULED",
        nullable=False
    )

    conflict = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
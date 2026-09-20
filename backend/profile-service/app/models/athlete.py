import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Athlete(Base):
    __tablename__ = "athletes"

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

    first_name = Column(
        String(100),
        nullable=False
    )

    last_name = Column(
        String(100),
        nullable=False
    )

    date_of_birth = Column(
        String(20),
        nullable=True
    )

    gender = Column(
        String(50),
        nullable=True
    )

    sport = Column(
        String(100),
        nullable=False,
        index=True
    )

    nationality = Column(
        String(100),
        nullable=True
    )

    profile_image_url = Column(
        Text,
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
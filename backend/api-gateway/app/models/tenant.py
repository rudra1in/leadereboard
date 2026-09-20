import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String(255),
        nullable=False,
        unique=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
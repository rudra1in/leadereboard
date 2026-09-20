import uuid

from sqlalchemy import Column, String, ForeignKey
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
        ForeignKey("tenants.id"),
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
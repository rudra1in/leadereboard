from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    event_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    sport: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    venue_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    court_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    participant_a_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    participant_b_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SCHEDULED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    payment_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    registration_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    order_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INR",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=PaymentStatus.PENDING.value,
    )

    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
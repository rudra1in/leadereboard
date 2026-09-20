from enum import Enum

from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class UserRole(str, Enum):
    FAN = "FAN"
    ATHLETE = "ATHLETE"
    ORGANIZER = "ORGANIZER"
    REFEREE = "REFEREE"
    ADMIN = "ADMIN"
    GATE_STAFF = "GATE_STAFF"


class User(Base):
    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
        default=UserRole.FAN.value,
    )

    tenant_id = Column(
        String,
        nullable=False,
        index=True,
    )
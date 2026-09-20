from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Integer
from app.database import Base


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)

    match_id = Column(String, unique=True, nullable=False, index=True)

    sport = Column(String, nullable=False)

    winner_id = Column(String, nullable=True)
    loser_id = Column(String, nullable=True)

    status = Column(String, nullable=False, default="PENDING")

    score = Column(JSON, nullable=True)

    statistics = Column(JSON, nullable=True)

    result_type = Column(String, nullable=True)

    verified_by = Column(String, nullable=True)
    verified_at = Column(DateTime, nullable=True)

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
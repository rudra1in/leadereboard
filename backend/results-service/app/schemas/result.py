from typing import Any, Optional
from pydantic import BaseModel


class ResultCreate(BaseModel):
    match_id: str
    sport: str

    winner_id: Optional[str] = None
    loser_id: Optional[str] = None

    status: str = "PENDING"

    score: Optional[dict[str, Any]] = None

    statistics: Optional[dict[str, Any]] = None

    result_type: Optional[str] = None


class ResultResponse(ResultCreate):
    id: int

    verified_by: Optional[str] = None

    class Config:
        from_attributes = True
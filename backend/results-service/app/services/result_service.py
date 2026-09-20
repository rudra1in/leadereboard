from datetime import datetime

from sqlalchemy.orm import Session

from app.models.result import Result
from app.schemas.result import ResultCreate


def create_result(
    db: Session,
    result_data: ResultCreate
):
    result = Result(
        match_id=result_data.match_id,
        sport=result_data.sport,
        winner_id=result_data.winner_id,
        loser_id=result_data.loser_id,
        status=result_data.status,
        score=result_data.score,
        statistics=result_data.statistics,
        result_type=result_data.result_type,
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    return result


def get_result(
    db: Session,
    match_id: str
):
    return (
        db.query(Result)
        .filter(Result.match_id == match_id)
        .first()
    )


def verify_result(
    db: Session,
    result: Result,
    verified_by: str
):
    result.status = "VERIFIED"
    result.verified_by = verified_by
    result.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(result)

    return result
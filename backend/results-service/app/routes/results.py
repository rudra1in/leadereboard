from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.result import ResultCreate, ResultResponse
from app.services.result_service import (
    create_result,
    get_result,
    verify_result,
)

router = APIRouter(
    prefix="/v1/results",
    tags=["Results"]
)


@router.post(
    "",
    response_model=ResultResponse
)
def create(
    result_data: ResultCreate,
    db: Session = Depends(get_db)
):
    existing = get_result(
        db,
        result_data.match_id
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Result already exists"
        )

    return create_result(
        db,
        result_data
    )


@router.get(
    "/{match_id}",
    response_model=ResultResponse
)
def get(
    match_id: str,
    db: Session = Depends(get_db)
):
    result = get_result(
        db,
        match_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )

    return result


@router.post(
    "/{match_id}/verify",
    response_model=ResultResponse
)
def verify(
    match_id: str,
    verified_by: str,
    db: Session = Depends(get_db)
):
    result = get_result(
        db,
        match_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Result not found"
        )

    return verify_result(
        db,
        result,
        verified_by
    )
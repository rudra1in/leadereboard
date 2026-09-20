from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match
from app.schemas import MatchCreate, MatchResponse, MatchStatus, MatchUpdate


router = APIRouter(
    prefix="/v1/matches",
    tags=["Matches"]
)


# --------------------------------------------------
# CREATE MATCH
# --------------------------------------------------

@router.post(
    "",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED
)
def create_match(
    match_data: MatchCreate,
    db: Session = Depends(get_db)
):
    match = Match(
        event_id=match_data.event_id,
        sport=match_data.sport,
        venue_id=match_data.venue_id,
        court_id=match_data.court_id,
        participant_a_id=match_data.participant_a_id,
        participant_b_id=match_data.participant_b_id,
        scheduled_at=match_data.scheduled_at,
        status=MatchStatus.SCHEDULED.value
    )

    db.add(match)
    db.commit()
    db.refresh(match)

    return match


# --------------------------------------------------
# GET MATCH
# --------------------------------------------------

@router.get(
    "/{match_id}",
    response_model=MatchResponse
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    match = db.get(Match, match_id)

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    return match


# --------------------------------------------------
# UPDATE MATCH
# --------------------------------------------------

@router.put(
    "/{match_id}",
    response_model=MatchResponse
)
def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db)
):
    match = db.get(Match, match_id)

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    # Don't allow updates to lifecycle through PUT

    if match_data.venue_id is not None:
        match.venue_id = match_data.venue_id

    if match_data.court_id is not None:
        match.court_id = match_data.court_id

    if match_data.scheduled_at is not None:
        match.scheduled_at = match_data.scheduled_at

    db.commit()
    db.refresh(match)

    return match


# --------------------------------------------------
# READY
# SCHEDULED → READY
# --------------------------------------------------

@router.post(
    "/{match_id}/ready",
    response_model=MatchResponse
)
def mark_match_ready(
    match_id: int,
    db: Session = Depends(get_db)
):
    match = db.get(Match, match_id)

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    if match.status != MatchStatus.SCHEDULED.value:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot mark match READY from {match.status}"
        )

    match.status = MatchStatus.READY.value

    db.commit()
    db.refresh(match)

    return match


# --------------------------------------------------
# START
# READY → LIVE
# --------------------------------------------------

@router.post(
    "/{match_id}/start",
    response_model=MatchResponse
)
def start_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    match = db.get(Match, match_id)

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    if match.status != MatchStatus.READY.value:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot start match from {match.status}"
        )

    match.status = MatchStatus.LIVE.value

    db.commit()
    db.refresh(match)

    return match


# --------------------------------------------------
# COMPLETE
# LIVE → COMPLETED
# --------------------------------------------------

@router.post(
    "/{match_id}/complete",
    response_model=MatchResponse
)
def complete_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    match = db.get(Match, match_id)

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    if match.status != MatchStatus.LIVE.value:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot complete match from {match.status}"
        )

    match.status = MatchStatus.COMPLETED.value

    db.commit()
    db.refresh(match)

    return match


# --------------------------------------------------
# VERIFY
# COMPLETED → VERIFIED
# --------------------------------------------------

@router.post(
    "/{match_id}/verify",
    response_model=MatchResponse
)
def verify_match(
    match_id: int,
    db: Session = Depends(get_db)
):
    match = db.get(Match, match_id)

    if not match:
        raise HTTPException(
            status_code=404,
            detail="Match not found"
        )

    if match.status != MatchStatus.COMPLETED.value:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot verify match from {match.status}"
        )

    match.status = MatchStatus.VERIFIED.value

    db.commit()
    db.refresh(match)

    return match
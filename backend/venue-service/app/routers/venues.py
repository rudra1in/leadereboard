from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.venue import Venue
from app.schemas.venue import (
    VenueCreate,
    VenueResponse,
    VenueUpdate,
)


router = APIRouter(
    prefix="/v1/venues",
    tags=["Venues"],
)


# Temporary development tenant.
# We will replace this with JWT tenant extraction.
DEMO_TENANT_ID = UUID(
    "00000000-0000-0000-0000-000000000001"
)


@router.post(
    "",
    response_model=VenueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_venue(
    venue_data: VenueCreate,
    db: Session = Depends(get_db),
):
    venue = Venue(
        tenant_id=DEMO_TENANT_ID,
        name=venue_data.name,
        description=venue_data.description,
        address=venue_data.address,
        city=venue_data.city,
        state=venue_data.state,
        country=venue_data.country,
        capacity=venue_data.capacity,
    )

    db.add(venue)
    db.commit()
    db.refresh(venue)

    return venue


@router.get(
    "",
    response_model=list[VenueResponse],
)
def get_venues(
    db: Session = Depends(get_db),
):
    venues = (
        db.query(Venue)
        .filter(
            Venue.tenant_id == DEMO_TENANT_ID
        )
        .all()
    )

    return venues


@router.get(
    "/{venue_id}",
    response_model=VenueResponse,
)
def get_venue(
    venue_id: UUID,
    db: Session = Depends(get_db),
):
    venue = (
        db.query(Venue)
        .filter(
            Venue.id == venue_id,
            Venue.tenant_id == DEMO_TENANT_ID,
        )
        .first()
    )

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    return venue


@router.put(
    "/{venue_id}",
    response_model=VenueResponse,
)
def update_venue(
    venue_id: UUID,
    venue_data: VenueUpdate,
    db: Session = Depends(get_db),
):
    venue = (
        db.query(Venue)
        .filter(
            Venue.id == venue_id,
            Venue.tenant_id == DEMO_TENANT_ID,
        )
        .first()
    )

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    update_data = venue_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(venue, field, value)

    db.commit()
    db.refresh(venue)

    return venue


@router.delete(
    "/{venue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_venue(
    venue_id: UUID,
    db: Session = Depends(get_db),
):
    venue = (
        db.query(Venue)
        .filter(
            Venue.id == venue_id,
            Venue.tenant_id == DEMO_TENANT_ID,
        )
        .first()
    )

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    db.delete(venue)
    db.commit()

    return None
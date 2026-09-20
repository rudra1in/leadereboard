import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import Event
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse
)


router = APIRouter(
    prefix="/v1/events",
    tags=["Events"]
)


# Temporary development tenant.
# Later this will come from the authenticated JWT.
DEV_TENANT_ID = uuid.UUID(
    "00000000-0000-0000-0000-000000000001"
)


@router.post(
    "",
    response_model=EventResponse,
    status_code=201
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db)
):
    event = Event(
        tenant_id=DEV_TENANT_ID,
        name=event_data.name,
        sport=event_data.sport,
        description=event_data.description,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        venue_id=event_data.venue_id,
        status=event_data.status,
        capacity=event_data.capacity
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get(
    "",
    response_model=list[EventResponse]
)
def get_events(
    db: Session = Depends(get_db)
):
    events = (
        db.query(Event)
        .filter(Event.tenant_id == DEV_TENANT_ID)
        .all()
    )

    return events


@router.get(
    "/{event_id}",
    response_model=EventResponse
)
def get_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.tenant_id == DEV_TENANT_ID
        )
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    return event


@router.put(
    "/{event_id}",
    response_model=EventResponse
)
def update_event(
    event_id: uuid.UUID,
    event_data: EventUpdate,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.tenant_id == DEV_TENANT_ID
        )
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    update_data = event_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


@router.delete(
    "/{event_id}",
    status_code=204
)
def delete_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.tenant_id == DEV_TENANT_ID
        )
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    db.delete(event)
    db.commit()

    return None
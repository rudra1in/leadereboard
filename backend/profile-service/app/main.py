import uuid

from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models.athlete import Athlete
from app.schemas.athlete import (
    AthleteCreate,
    AthleteResponse,
    AthleteUpdate,
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GameX Profile Service",
    version="1.0.0"
)


def get_tenant_id(
    x_tenant_id: str = Header(...)
) -> uuid.UUID:
    try:
        return uuid.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid X-Tenant-ID"
        )


@app.get("/health")
def health():
    return {
        "service": "profile-service",
        "status": "running"
    }


@app.post(
    "/v1/athletes",
    response_model=AthleteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_athlete(
    athlete_data: AthleteCreate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    athlete = Athlete(
        tenant_id=tenant_id,
        first_name=athlete_data.first_name,
        last_name=athlete_data.last_name,
        date_of_birth=athlete_data.date_of_birth,
        gender=athlete_data.gender,
        sport=athlete_data.sport,
        nationality=athlete_data.nationality,
        profile_image_url=athlete_data.profile_image_url
    )

    db.add(athlete)
    db.commit()
    db.refresh(athlete)

    return athlete


@app.get(
    "/v1/athletes",
    response_model=list[AthleteResponse]
)
def get_athletes(
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    athletes = (
        db.query(Athlete)
        .filter(Athlete.tenant_id == tenant_id)
        .order_by(Athlete.created_at.desc())
        .all()
    )

    return athletes


@app.get(
    "/v1/athletes/{athlete_id}",
    response_model=AthleteResponse
)
def get_athlete(
    athlete_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    athlete = (
        db.query(Athlete)
        .filter(
            Athlete.id == athlete_id,
            Athlete.tenant_id == tenant_id
        )
        .first()
    )

    if not athlete:
        raise HTTPException(
            status_code=404,
            detail="Athlete not found"
        )

    return athlete


@app.put(
    "/v1/athletes/{athlete_id}",
    response_model=AthleteResponse
)
def update_athlete(
    athlete_id: uuid.UUID,
    athlete_data: AthleteUpdate,
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    athlete = (
        db.query(Athlete)
        .filter(
            Athlete.id == athlete_id,
            Athlete.tenant_id == tenant_id
        )
        .first()
    )

    if not athlete:
        raise HTTPException(
            status_code=404,
            detail="Athlete not found"
        )

    update_data = athlete_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(athlete, field, value)

    db.commit()
    db.refresh(athlete)

    return athlete
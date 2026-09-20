from fastapi import FastAPI

from app.database import Base, engine
from app.models.venue import Venue
from app.routers.venues import router as venue_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GameX Venue Service",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "service": "venue-service",
        "status": "running",
    }


app.include_router(venue_router)
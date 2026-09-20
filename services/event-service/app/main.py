from fastapi import FastAPI

from app.database import Base, engine
from app.models.event import Event
from app.routers.events import router as events_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GameX Event Service",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "service": "event-service",
        "status": "running"
    }


app.include_router(events_router)
from fastapi import FastAPI

from app.database import Base, engine
from app.routes.schedules import router as schedule_router

from app.models.schedule import Schedule


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GameX Scheduling Service",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "service": "scheduling-service",
        "status": "running"
    }


app.include_router(schedule_router)
from fastapi import FastAPI

from app.database import Base, engine
from app.routes.results import router as results_router

from app.models.result import Result


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GameX Results Service",
    version="1.0.0"
)


app.include_router(results_router)


@app.get("/")
def root():
    return {
        "service": "results-service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
from fastapi import FastAPI

from app.database import Base, engine
from app.routes.matches import router as match_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GameX Match Service",
    version="1.0.0"
)


app.include_router(match_router)


@app.get("/")
def root():
    return {
        "service": "match-service",
        "status": "running"
    }
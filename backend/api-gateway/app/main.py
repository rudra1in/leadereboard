from fastapi import FastAPI

from app.auth.models import Base
from app.auth.routes import router as auth_router
from app.database import engine
from app.users.routes import router as users_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GameX API Gateway",
    description=(
        "Authoritative backend API gateway "
        "for the GameX sports platform"
    ),
    version="1.0.0",
)


# Authentication routes
app.include_router(auth_router)

# User routes
app.include_router(users_router)


@app.get("/")
def root():
    return {
        "service": "GameX API Gateway",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }

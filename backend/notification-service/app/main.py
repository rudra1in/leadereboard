from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service", version="0.1.0")

class NotifyRequest(BaseModel):
    registration_id: str
    email: EmailStr
    full_name: str
    message: str | None = None

@app.post("/notify")
async def notify(req: NotifyRequest):
    # TODO: real email/SMS/push provider
    logger.info(
        f"Notification sent | registration_id={req.registration_id} "
        f"email={req.email} name={req.full_name}"
    )
    return {
        "status": "sent",
        "registration_id": req.registration_id,
        "channel": "email"
    }
from fastapi import Request

@app.middleware("http")
async def log_incoming_requests(request: Request, call_next):
    print(f">>> [DEBUG RAW REQUEST] Method: {request.method} | URL: {request.url.path}")
    response = await call_next(request)
    print(f">>> [DEBUG RAW RESPONSE] Status: {response.status_code}")
    return response

@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification-service"}
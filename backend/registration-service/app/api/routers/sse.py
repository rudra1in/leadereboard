import asyncio
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.consumers.sse_broadcaster import sse_clients

router = APIRouter(prefix="/sse", tags=["sse"])

@router.get("/registrations/{registration_id}")
async def registration_events(registration_id: str, request: Request):
    queue = asyncio.Queue()
    sse_clients[registration_id] = queue

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": "registration_update",
                        "data": data
                    }
                except asyncio.TimeoutError:
                    # Keep-alive
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            sse_clients.pop(registration_id, None)

    return EventSourceResponse(event_generator())
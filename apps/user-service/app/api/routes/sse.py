import asyncio
from datetime import datetime
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/sse", tags=["sse"])

@router.get("/events")
async def sse_events(request: Request):
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                yield {
                    "event": "heartbeat",
                    "data": {
                        "message": "alive",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                }
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())

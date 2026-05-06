import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.app_state import get_sse_queue

router = APIRouter()


@router.get("/status/stream")
async def status_stream():
    queue = await get_sse_queue()

    async def event_generator():
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=25)
                data = json.dumps(item["data"])
                yield f"event: {item['event']}\ndata: {data}\n\n"
            except asyncio.TimeoutError:
                yield "event: heartbeat\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

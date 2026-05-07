import asyncio
from typing import Optional

# SSE broadcast queue — one queue shared across all clients
_sse_queue: asyncio.Queue = asyncio.Queue()

# Latest uploaded file path (for create_notebooklm)
uploaded_file_path: Optional[str] = None

# Latest upload state — survives page refresh
last_filename: Optional[str] = None
last_chunk_count: int = 0


async def broadcast(event: str, data: dict) -> None:
    await _sse_queue.put({"event": event, "data": data})


async def get_sse_queue() -> asyncio.Queue:
    return _sse_queue

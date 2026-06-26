"""GET /events — Server-Sent Events stream. Pages subscribe and refetch live, so
a citizen report or screened call lights up the graph/map/analytics with no refresh.
"""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.events import broker

router = APIRouter(tags=["events"])


@router.get("/events")
async def events(request: Request) -> StreamingResponse:
    q = broker.subscribe()

    async def gen():
        # tell the client we're live
        yield "retry: 3000\n\n"
        yield 'data: {"type":"hello"}\n\n'
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"   # heartbeat comment
        finally:
            broker.unsubscribe(q)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

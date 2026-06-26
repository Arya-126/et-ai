"""In-process event broker for real-time (SSE) updates. The pipeline runs in a
threadpool (sync), while SSE consumers live on the event loop — so publish() must
be thread-safe. We capture the running loop at startup and fan out via
loop.call_soon_threadsafe.
"""
from __future__ import annotations

import asyncio
import logging

log = logging.getLogger("events")


class EventBroker:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.discard(q)

    def publish(self, event: dict) -> None:
        """Safe to call from sync (threadpool) or async code."""
        if self._loop is None:
            return
        for q in list(self._subscribers):
            try:
                self._loop.call_soon_threadsafe(q.put_nowait, event)
            except Exception:  # noqa: BLE001 — a full/closed queue must never break the request
                pass


broker = EventBroker()


def publish(event: dict) -> None:
    broker.publish(event)

"""Win-feature upgrades: impact ROI, SSE broker, OCR graceful degradation."""
import json
import os

import pytest

from app.agents.registry import registry
from app.graph.factory import get_store
from app.schema import Report

DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reports.json")


def _seed():
    if not os.path.exists(DATA):
        pytest.skip("run `python -m data.generate` first")
    with open(DATA, encoding="utf-8") as f:
        raw = json.load(f)
    store = get_store()
    store.reset()
    for d in raw:
        store.write_report(Report(**d))


def test_impact_money_saved_positive():
    _seed()
    registry.reset()
    from app.routers.impact import impact
    out = impact()
    assert out["high_risk_intercepted"] > 0
    assert out["money_at_risk_saved"] > 0
    assert out["national_annual_projection"] > out["money_at_risk_saved"]


def test_event_broker_delivers():
    import asyncio

    from app.events import broker

    async def run():
        broker.bind_loop(asyncio.get_running_loop())
        q = broker.subscribe()
        broker.publish({"type": "report", "verdict": "HIGH RISK"})
        await asyncio.sleep(0)            # let call_soon_threadsafe run
        evt = await asyncio.wait_for(q.get(), timeout=2)
        broker.unsubscribe(q)
        return evt

    evt = asyncio.run(run())
    assert evt["type"] == "report"


def test_ocr_degrades_gracefully():
    # easyocr isn't installed in CI/most envs — extract_text must return None, not raise.
    from cv import ocr
    assert ocr.extract_text(b"not-an-image") is None

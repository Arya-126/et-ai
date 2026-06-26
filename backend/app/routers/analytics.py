"""Analytics & trends — command-centre stats over all processed reports.
GET /analytics -> breakdowns (scam type, verdict, channel, language, district) +
a daily time series + alert counts.
"""
from __future__ import annotations

from collections import Counter

from fastapi import APIRouter

from app.agents.alerting import store as alert_store
from app.agents.registry import registry

router = APIRouter(tags=["analytics"])


def _top(counter: Counter, n: int | None = None) -> list[dict]:
    items = counter.most_common(n)
    return [{"label": k or "—", "count": v} for k, v in items]


@router.get("/analytics/summary")
def analytics() -> dict:
    reports = registry.all()
    by_type, by_verdict, by_channel, by_lang, by_district, by_day = (
        Counter() for _ in range(6)
    )
    for r in reports:
        if r.verdict and r.verdict != "LIKELY SAFE":
            by_type[r.scam_type or "Unknown"] += 1
        by_verdict[r.verdict or "Unknown"] += 1
        by_channel[r.channel] += 1
        by_lang[r.language or "en"] += 1
        if r.district:
            by_district[r.district] += 1
        if r.timestamp:
            by_day[r.timestamp.date().isoformat()] += 1

    alerts = alert_store.all()
    return {
        "total_reports": len(reports),
        "scam_types": _top(by_type),
        "verdicts": _top(by_verdict),
        "channels": _top(by_channel),
        "languages": _top(by_lang),
        "top_districts": _top(by_district, 8),
        "timeseries": [{"day": d, "count": c} for d, c in sorted(by_day.items())],
        "alerts": {
            "total": len(alerts),
            "by_kind": _top(Counter(a.kind for a in alerts)),
        },
    }

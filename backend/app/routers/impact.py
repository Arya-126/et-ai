"""GET /impact — Business-impact / ROI estimate from intercepted HIGH-RISK cases.
Money-at-risk is Σ avg-loss over HIGH-RISK reports (disclosed assumptions)."""
from __future__ import annotations

from fastapi import APIRouter

from app.agents.alerting import store as alert_store
from app.agents.registry import registry
from data.impact_assumptions import (AVG_RESPONSE_SECONDS, NATIONAL_DAILY_COMPLAINTS,
                                      SOURCES_NOTE, avg_loss)

router = APIRouter(tags=["impact"])


@router.get("/impact/summary")
def impact() -> dict:
    reports = registry.all()
    high = [r for r in reports if r.verdict == "HIGH RISK"]
    money_saved = sum(avg_loss(r.scam_type) for r in high)

    # Projection: if this loop ran on the national complaint stream, scale the
    # per-report money-at-risk we already intercept here.
    per_report = (money_saved / len(high)) if high else 0
    national_annual = int(per_report * NATIONAL_DAILY_COMPLAINTS * 365)

    return {
        "high_risk_intercepted": len(high),
        "victims_protected": len(high),
        "money_at_risk_saved": money_saved,        # ₹
        "avg_response_seconds": AVG_RESPONSE_SECONDS,
        "alerts_generated": len(alert_store.all()),
        "national_annual_projection": national_annual,   # ₹
        "disclaimer": SOURCES_NOTE,
    }

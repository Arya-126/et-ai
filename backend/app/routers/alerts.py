"""Alert endpoints (Component 1).
GET /alerts          -> all generated MHA/telecom alerts (newest first)
GET /alerts/{id}/pdf -> the alert artifact PDF
"""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.agents.alerting import store
from app.reporting.alert_pdf import build_alert_pdf
from app.schema import Alert

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=list[Alert])
def list_alerts() -> list[Alert]:
    return store.all()


@router.get("/alerts/{alert_id}/pdf")
def alert_pdf(alert_id: str):
    alert = store.get(alert_id)
    if alert is None:
        raise HTTPException(404, f"Alert {alert_id} not found")
    path = build_alert_pdf(alert)
    if not os.path.exists(path):
        raise HTTPException(500, "Failed to render alert PDF")
    return FileResponse(path, media_type="application/pdf",
                        filename=f"alert_{alert_id}.pdf")

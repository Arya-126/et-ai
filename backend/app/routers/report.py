"""Citizen entry point.
POST /report            -> run the pipeline, return enriched Report (verdict, alert)
POST /report/complaint  -> draft an NCRB / cybercrime.gov.in complaint PDF
GET  /languages         -> supported languages for the Citizen Shield selector
"""
from __future__ import annotations

import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.agents.pipeline import process_report
from app.reporting.complaint_pdf import build_complaint_pdf
from app.schema import Report, ReportInput
from data.i18n import LANGUAGES

router = APIRouter(tags=["citizen"])


@router.post("/report", response_model=Report)
def submit_report(inp: ReportInput) -> Report:
    return process_report(inp)


@router.post("/report/complaint")
def report_complaint(report: Report):
    path = build_complaint_pdf(report)
    return FileResponse(
        path, media_type="application/pdf",
        filename=f"complaint_{report.report_id}.pdf",
    )


@router.get("/languages")
def languages() -> dict[str, str]:
    return LANGUAGES

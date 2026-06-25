"""POST /report — the citizen entry point. Runs the LangGraph pipeline and
returns the enriched Report (verdict block + entities)."""
from __future__ import annotations

from fastapi import APIRouter

from app.agents.pipeline import process_report
from app.schema import Report, ReportInput

router = APIRouter(tags=["citizen"])


@router.post("/report", response_model=Report)
def submit_report(inp: ReportInput) -> Report:
    return process_report(inp)

"""Call Guard — screen a (possibly unsaved) phone call for fraud.

POST /call/screen     -> classify the call transcript + check the caller number
                         against the fraud graph; a known number forces HIGH RISK.
GET  /call/blocklist  -> known scammer numbers mined live from the graph.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.agents import alerting, reputation
from app.agents.pipeline import process_report
from app.schema import CallInput, CallScreenResult, NumberReputation, ReportInput

router = APIRouter(tags=["call-guard"])


@router.post("/call/screen", response_model=CallScreenResult)
def screen_call(call: CallInput) -> CallScreenResult:
    # Reputation BEFORE we write this call, so it reflects prior knowledge.
    rep = reputation.lookup(call.caller_number)

    inp = ReportInput(
        raw_text=call.transcript,
        channel="call",
        phone=call.caller_number,
        caller_is_known=call.is_saved,
        language=call.language,
        district=call.district,
    )
    report = process_report(inp)   # classify -> graph write -> maybe alert

    # Known-number override: a caller already in the fraud graph is a known
    # scammer, so the call is HIGH RISK regardless of what the transcript says.
    if rep.known and report.verdict != "HIGH RISK":
        report.verdict = "HIGH RISK"
        report.confidence = max(report.confidence or 0.0, 0.95)
        flag = (
            f"Caller {call.caller_number} is a KNOWN scammer number — linked to "
            f"{rep.report_count} prior report(s)"
            + (f", inside fraud ring {rep.ring_id}" if rep.in_ring else "") + "."
        )
        report.red_flags = [flag, *report.red_flags]
        if report.scam_type in (None, "No clear scam pattern") and rep.scam_types:
            report.scam_type = rep.scam_types[0]
        report.alert = alerting.maybe_alert(report)

    return CallScreenResult(report=report, reputation=rep)


@router.get("/call/blocklist", response_model=list[NumberReputation])
def blocklist() -> list[NumberReputation]:
    return reputation.blocklist()

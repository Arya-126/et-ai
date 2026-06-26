"""AlertingAgent (Component 1) — on a HIGH RISK digital-arrest verdict, generate
escalation artifacts *before money moves*: an MHA/I4C cybercrime alert and a
telecom block/monitor flag for the spoofed number. Kept in an in-process store
the dashboard reads.

These are demonstration artifacts (no real MHA/telecom integration exists), but
they are the concrete "automated alert generation" the brief asks for.
"""
from __future__ import annotations

import re

from app.schema import Alert, Report

# crude carrier guess from an Indian mobile number, for a believable telecom target
_CARRIERS = ["Jio", "Airtel", "Vi", "BSNL"]


def _carrier_for(phone: str | None) -> str:
    if not phone:
        return "Unknown carrier"
    digits = re.sub(r"\D", "", phone)[-10:]
    return _CARRIERS[int(digits[0]) % len(_CARRIERS)] if digits else "Unknown carrier"


def _is_digital_arrest(report: Report) -> bool:
    text = (report.raw_text or "").lower()
    st = (report.scam_type or "").lower()
    return (
        "digital arrest" in text
        or "digital arrest" in st
        or "impersonation" in st
        or bool(report.claimed_authority)
        or report.matched_script_id in {"digital_arrest_cbi", "ed_money_laundering",
                                        "trai_disconnect", "police_cyber_cell"}
    )


class AlertStore:
    """Process-wide list of generated alerts."""

    def __init__(self) -> None:
        self._alerts: list[Alert] = []

    def add(self, alert: Alert) -> None:
        self._alerts.append(alert)

    def all(self) -> list[Alert]:
        return list(reversed(self._alerts))   # newest first

    def get(self, alert_id: str) -> Alert | None:
        return next((a for a in self._alerts if a.alert_id == alert_id), None)

    def reset(self) -> None:
        self._alerts.clear()


store = AlertStore()


def maybe_alert(report: Report) -> Alert | None:
    """On HIGH RISK: always raise a trusted-contact (family) alert; for
    digital-arrest also raise MHA + telecom alerts. Returns the primary alert to
    attach to the report (MHA if digital-arrest, else the CONTACT alert)."""
    if report.verdict != "HIGH RISK":
        return None

    # Trusted-contact alert — protects the elderly-victim case: loop in family fast.
    contact = Alert(
        report_id=report.report_id,
        kind="CONTACT",
        target="Trusted contact (family)",
        summary=(
            f"Likely {report.scam_type or 'scam'} targeting your relative"
            f"{' on a call from ' + report.phone if report.phone else ''}. "
            f"Please call them now — tell them not to transfer money or share any OTP."
        ),
        scam_type=report.scam_type,
        phone=report.phone,
        district=report.district,
    )
    store.add(contact)

    if not _is_digital_arrest(report):
        return contact

    mha = Alert(
        report_id=report.report_id,
        kind="MHA",
        target="I4C / MHA Cybercrime Coordination Centre",
        summary=(
            f"Active digital-arrest scam session flagged in {report.district or 'unknown district'}. "
            f"Impersonated authority: {report.claimed_authority or 'unspecified'}. "
            f"Intervene before transfer."
        ),
        scam_type=report.scam_type,
        phone=report.phone,
        upi_id=report.upi_id,
        district=report.district,
    )
    store.add(mha)

    if report.phone:
        store.add(Alert(
            report_id=report.report_id,
            kind="TELECOM",
            target=f"Telecom: {_carrier_for(report.phone)}",
            summary=f"Block/monitor request for spoofed controller number {report.phone}.",
            scam_type=report.scam_type,
            phone=report.phone,
            district=report.district,
        ))
    return mha

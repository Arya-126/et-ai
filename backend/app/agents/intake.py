"""IntakeAgent — deterministic, no LLM. Normalizes whatever the citizen pasted
(free text, SMS, OCR'd screenshot) into entities on the Report. Fast and
predictable so the graph keys are clean.
"""
from __future__ import annotations

import re

from app.schema import Report, ReportInput

_UPI = re.compile(r"\b([a-z0-9._-]{2,}@[a-z]{2,})\b", re.I)
_PHONE = re.compile(r"(?:(?:\+?91[\-\s]?)|0)?([6-9]\d{9})\b")
_ACCOUNT = re.compile(r"\b(\d{11,16})\b")
_AUTHORITY = [
    ("CBI", re.compile(r"\bcbi\b", re.I)),
    ("ED", re.compile(r"\b(ed|enforcement directorate)\b", re.I)),
    ("Customs", re.compile(r"\bcustoms\b", re.I)),
    ("TRAI", re.compile(r"\btrai\b", re.I)),
    ("Police", re.compile(r"\b(police|cyber cell)\b", re.I)),
    ("Narcotics", re.compile(r"\bnarcotics\b", re.I)),
    ("Bank", re.compile(r"\b(bank|kyc)\b", re.I)),
]


def _normalize_phone(raw: str) -> str:
    return "+91" + raw  # demo dataset is India-only


def intake(inp: ReportInput) -> Report:
    text = inp.raw_text.strip()

    upi = _UPI.search(text)
    phone = _PHONE.search(text)
    # avoid mistaking a UPI's local part or a 10-digit phone for an account no
    account = None
    for m in _ACCOUNT.finditer(text):
        digits = m.group(1)
        if len(digits) >= 11:
            account = digits
            break

    authority = next((name for name, pat in _AUTHORITY if pat.search(text)), None)

    return Report(
        raw_text=text,
        channel=inp.channel,
        claimed_authority=authority,
        phone=_normalize_phone(phone.group(1)) if phone else None,
        upi_id=upi.group(1).lower() if upi else None,
        account_no=account,
        reporter_id=inp.reporter_id,
        district=inp.district,
        language=inp.language,
        video_call=bool(re.search(r"video\s*call", text, re.I)) or None,
    )

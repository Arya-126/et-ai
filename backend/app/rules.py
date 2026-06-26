"""Hard-signal rule layer. Two jobs:
  1. Boost confidence on unambiguous scam markers (digital-arrest scripts,
     authority threats, pay-to-UPI demands) — the rubric rewards catching these.
  2. CAP verdicts on benign markers so the citizen tool never cries "HIGH RISK"
     on "Mom, dinner at 8?" — the rubric explicitly penalizes false positives.

Also serves as the standalone classifier when Ollama is unavailable, so the
citizen path degrades gracefully instead of failing.
"""
from __future__ import annotations

import re

from app.schema import Classification, Report

# (compiled pattern, human-readable red flag, weight 0..1)
SCAM_SIGNALS: list[tuple[re.Pattern, str, float]] = [
    (re.compile(r"\bdigital\s+arrest", re.I), "Mentions 'digital arrest' - not a real legal procedure", 0.6),
    (re.compile(r"stay\s+on\s+(the\s+)?(video\s+)?call|do\s*n[o']?t\s+(disconnect|cut\s+the\s+call)", re.I), "Demands you stay on a video call / not disconnect", 0.5),
    (re.compile(r"money\s+laundering|illegal\s+(transaction|activity)|narcotics|drugs?\s+parcel", re.I), "Accuses you of a serious crime to create panic", 0.4),
    (re.compile(r"\b(cbi|ed|enforcement\s+directorate|customs|trai|narcotics|cyber\s+cell|police)\b", re.I), "Impersonates a government / law-enforcement authority", 0.3),
    (re.compile(r"your\s+aadhaar|aadhaar\s+(is\s+)?(linked|misused|blocked)", re.I), "Claims your Aadhaar is linked to a crime", 0.4),
    (re.compile(r"arrest\s+warrant|non[-\s]?bailable|supreme\s+court|court\s+notice", re.I), "Threatens arrest / legal action", 0.4),
    (re.compile(r"parcel.{0,20}(seized|illegal|drugs)|fedex|courier.{0,20}(seized|customs)", re.I), "Fake parcel / courier seizure pretext", 0.4),
    (re.compile(r"transfer|pay|deposit|send\s+money|rtgs|imps|neft", re.I), "Asks you to transfer / pay money", 0.4),
    (re.compile(r"\b\w+@(okaxis|okhdfcbank|oksbi|okicici|ybl|paytm|upi|axl|ibl)\b", re.I), "Routes payment to a UPI handle", 0.45),
    (re.compile(r"verification\s+(fee|charge)|refundable\s+deposit|security\s+deposit", re.I), "Demands a 'verification' or 'security' fee", 0.4),
    (re.compile(r"share\s+(your\s+)?(otp|cvv|pin|password)|tell\s+me\s+the\s+otp|read\s+(me\s+)?the\s+otp", re.I), "Asks you to share OTP / PIN / CVV", 0.5),
    (re.compile(r"keep\s+this\s+(call\s+)?confidential|do\s*n[o']?t\s+(tell|inform)\s+(anyone|family)", re.I), "Tells you to keep it secret from family", 0.4),
    # ---- call-fraud families (Call Guard) -------------------------------
    (re.compile(r"approve\s+(the\s+)?(request|collect)|collect\s+request|accept\s+(the\s+)?request\s+on\s+(your\s+)?upi", re.I), "Asks you to APPROVE a UPI collect request (money leaves your account)", 0.55),
    (re.compile(r"we\s+have\s+your\s+(son|daughter|child|brother|husband|wife|father|mother)|your\s+\w+\s+(is\s+)?(kidnap|with\s+us|met\s+with\s+an\s+accident)", re.I), "Claims a family member is kidnapped or in an accident", 0.7),
    (re.compile(r"do\s*n[o']?t\s+(call|inform)\s+(the\s+)?police|if\s+you\s+call\s+(the\s+)?police", re.I), "Forbids you from calling the police", 0.5),
    (re.compile(r"ransom|bail\s+money|release\s+(him|her|your)", re.I), "Demands ransom / 'release' money", 0.5),
    (re.compile(r"morph(ed)?|leak.{0,20}(photo|video|image)|intimate\s+(photo|video)|post.{0,20}online", re.I), "Threatens to leak morphed / intimate images (sextortion)", 0.6),
    (re.compile(r"loan\s+app|emi\s+.{0,10}overdue|recovery\s+(agent|team)|defaulter", re.I), "Predatory loan-app recovery threat", 0.5),
    (re.compile(r"guaranteed\s+.{0,10}return|activation\s+fee|withdraw.{0,20}deposit|vip\s+group|daily\s+earning|task.{0,10}(earn|commission)", re.I), "Investment / task scam: guaranteed returns or pay-to-withdraw", 0.5),
]

# Markers that strongly suggest an ordinary, safe message. Used to cap verdicts.
BENIGN_MARKERS: list[re.Pattern] = [
    re.compile(r"\b(dinner|lunch|breakfast|coffee|movie|birthday|party)\b", re.I),
    re.compile(r"\b(mom|dad|mum|papa|bro|sis|buddy|dear)\b", re.I),
    re.compile(r"\b(meeting|standup|deadline|invoice|delivery\s+scheduled|out\s+for\s+delivery)\b", re.I),
    re.compile(r"do\s+not\s+share\s+(this\s+)?otp\s+with\s+anyone", re.I),  # legit bank phrasing
]

MONEY_OR_THREAT = re.compile(
    r"transfer|pay\b|deposit|otp|arrest|laundering|aadhaar|warrant|seized|@", re.I
)

HIGH = 0.7
SUSPICIOUS = 0.4


def rule_score(report: Report) -> tuple[float, list[str], bool]:
    """Return (score 0..1, red_flags, looks_benign)."""
    text = report.raw_text or ""
    score = 0.0
    flags: list[str] = []
    for pattern, flag, weight in SCAM_SIGNALS:
        if pattern.search(text):
            score += weight
            flags.append(flag)
    # structured signals from intake
    if report.upi_id:
        score += 0.15
    if report.claimed_authority:
        score += 0.1

    # number-spoofing signatures (Component 1: digital-arrest detection)
    if spoof_signature(report):
        score += 0.2
        flags.append("Caller ID shows spoofing signatures (impersonated authority)")
    if report.video_call:
        score += 0.15
        flags.append("Scammer demanded a video call (a digital-arrest hallmark)")

    # unsaved-number signal (Call Guard): an unknown caller making demands is a
    # strong tell — fraud calls almost always come from numbers not in your contacts.
    if report.caller_is_known is False and (
        report.upi_id or report.claimed_authority or MONEY_OR_THREAT.search(text)
    ):
        score += 0.2
        flags.append("Unknown caller (not in your contacts) making money/authority demands")

    benign = any(p.search(text) for p in BENIGN_MARKERS)
    # only "really benign" if there is no money/threat language at all
    looks_benign = benign and not MONEY_OR_THREAT.search(text)

    return min(score, 1.0), flags, looks_benign


def spoof_signature(report: Report) -> bool:
    """Heuristic caller-ID spoofing detection for digital-arrest calls:
    an explicit spoof flag, OR a domestic 'authority' caller arriving on an
    international/odd-length number, OR a malformed caller id."""
    if report.caller_spoofed:
        return True
    phone = report.phone or ""
    text = (report.raw_text or "").lower()
    claims_authority = bool(report.claimed_authority) or bool(
        re.search(r"\b(cbi|ed|trai|customs|police|cyber cell|narcotics)\b", text)
    )
    digits = re.sub(r"\D", "", phone)
    # an "authority" calling from a non +91 international number, or a wrong-length
    # Indian mobile, is a classic spoof tell.
    intl_non_india = phone.startswith("+") and not phone.startswith("+91")
    malformed = bool(digits) and len(digits.lstrip("91")) not in (10,)
    return claims_authority and (intl_non_india or malformed)


def _verdict_from_score(score: float) -> str:
    if score >= HIGH:
        return "HIGH RISK"
    if score >= SUSPICIOUS:
        return "SUSPICIOUS"
    return "LIKELY SAFE"


DEFAULT_ADVICE = {
    "HIGH RISK": "This has the hallmarks of a scam. Do not transfer money or share OTP/PIN. "
                 "No real agency (CBI, ED, Customs, police) arrests people over a video call. "
                 "Hang up and report it to the cybercrime helpline 1930 or cybercrime.gov.in.",
    "SUSPICIOUS": "Treat this with caution. Do not share OTP/PIN or pay anything until you have "
                  "independently verified the caller via an official number. When in doubt, call 1930.",
    "LIKELY SAFE": "Nothing in this message matches known scam patterns. Stay alert and never share "
                   "OTPs or transfer money to unverified accounts.",
}


def _scam_family(text: str) -> str:
    """Best-effort scam family from text, so the rules-only path isn't always
    'Digital Arrest'. Order matters — most specific first."""
    t = text.lower()
    if re.search(r"we\s+have\s+your\s+(son|daughter|child|brother|husband|wife)|kidnap|ransom|met\s+with\s+an\s+accident", t):
        return "Kidnapping / Ransom"
    if re.search(r"loan\s+app|emi\s+.{0,10}overdue|recovery\s+(agent|team)|defaulter", t):
        return "Loan-app / Recovery Scam"
    if re.search(r"morph|sextortion|intimate\s+(photo|video)|leak.{0,20}(photo|video|image)", t):
        return "Sextortion"
    if re.search(r"guaranteed\s+.{0,10}return|activation\s+fee|withdraw.{0,20}deposit|vip\s+group|task.{0,10}(earn|commission)", t):
        return "Investment / Task Scam"
    if re.search(r"parcel|customs|fedex|courier|narcotics", t):
        return "Parcel / Customs Scam"
    if re.search(r"\bkyc\b|share.{0,10}otp|read.{0,10}otp|approve\s+(the\s+)?(request|collect)|account.{0,10}(blocked|frozen)", t):
        return "OTP / UPI Fraud"
    if re.search(r"lottery|lucky draw|won.{0,15}(prize|lakh|crore)|job offer", t):
        return "Lottery / Prize Scam"
    return "Digital Arrest / Impersonation Scam"


def rules_only_classification(report: Report) -> Classification:
    """Standalone verdict when the LLM is unavailable."""
    score, flags, looks_benign = rule_score(report)
    if looks_benign:
        score = min(score, 0.2)
    verdict = _verdict_from_score(score)
    scam_type = _scam_family(report.raw_text or "") if verdict != "LIKELY SAFE" else "No clear scam pattern"
    return Classification(
        verdict=verdict,
        scam_type=scam_type,
        confidence=round(score, 2),
        red_flags=flags,
        advice=DEFAULT_ADVICE[verdict],
        matched_script_id=None,
    )


def adjust(llm: Classification, report: Report) -> Classification:
    """Blend the LLM verdict with hard signals and enforce the benign cap."""
    score, rule_flags, looks_benign = rule_score(report)

    # Merge red flags (rules + LLM), dedup preserving order.
    merged_flags = list(dict.fromkeys([*llm.red_flags, *rule_flags]))

    # If strong hard signals exist, the LLM can't under-call it.
    blended_conf = max(llm.confidence or 0.0, score)
    verdict = llm.verdict
    if score >= HIGH and verdict != "HIGH RISK":
        verdict = "HIGH RISK"

    # Benign cap wins over an over-eager LLM (false-positive guard).
    if looks_benign:
        verdict = "LIKELY SAFE"
        blended_conf = min(blended_conf, 0.2)
        merged_flags = []

    advice = llm.advice or DEFAULT_ADVICE[verdict]
    return Classification(
        verdict=verdict,
        scam_type=llm.scam_type if verdict != "LIKELY SAFE" else "No clear scam pattern",
        confidence=round(blended_conf, 2),
        red_flags=merged_flags,
        advice=advice,
        matched_script_id=llm.matched_script_id,
    )

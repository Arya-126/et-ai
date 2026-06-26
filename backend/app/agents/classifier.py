"""ClassifierAgent — Ollama few-shot over the scam-script library, then the
hard-signal rule layer adjusts the verdict (boost on strong signals, cap on
benign). If Ollama is unavailable, fall back to a rules-only verdict so the
citizen path never hard-fails.
"""
from __future__ import annotations

import logging

from app import rules
from app.llm import LLMUnavailable, chat_json
from app.schema import Classification, Report
from data.scam_scripts import SCRIPTS_BY_ID, few_shot_block

log = logging.getLogger("classifier")

SYSTEM_PROMPT = f"""You are a fraud-triage assistant for Indian citizens. Classify a single
message or call transcript the citizen received. You are NOT the scammer — you protect the user.

Return STRICT JSON with exactly these keys:
  "verdict": one of "HIGH RISK", "SUSPICIOUS", "LIKELY SAFE"
  "scam_type": short label, one of: "Digital Arrest / Impersonation Scam", "Parcel / Customs Scam",
       "OTP / UPI Fraud", "Kidnapping / Ransom", "Sextortion", "Loan-app / Recovery Scam",
       "Investment / Task Scam", "Lottery / Prize Scam", or "No clear scam pattern"
  "confidence": number 0.0-1.0
  "red_flags": array of short strings explaining WHY (empty if safe)
  "advice": one clear, calm paragraph of what the citizen should do
  "matched_script_id": the closest known script id, or null

Known scam scripts (HIGH RISK exemplars):
{few_shot_block()}

Valid matched_script_id values: {list(SCRIPTS_BY_ID.keys())}

Rules of judgement:
- "Digital arrest", staying on a video call, threats from CBI/ED/Customs/TRAI/police,
  Aadhaar-linked-to-crime, demands to transfer money or share OTP => HIGH RISK.
- Asking you to share an OTP or APPROVE a UPI collect request => OTP / UPI Fraud, HIGH RISK.
- "We have your son/daughter", kidnap, accident + don't-call-police + pay now => Kidnapping / Ransom, HIGH RISK.
- Threats to leak morphed/intimate images unless paid => Sextortion, HIGH RISK.
- Loan-app recovery threats to shame you to your contacts => Loan-app / Recovery Scam, HIGH RISK.
- Guaranteed returns / pay-a-fee-to-withdraw / task-earning bait => Investment / Task Scam, HIGH RISK.
- An unknown/unsaved caller making any money or authority demand is a strong scam signal.
- Ordinary personal/work messages (family plans, meetings, legitimate delivery notices,
  banks telling you NOT to share your OTP) => LIKELY SAFE. Do NOT over-flag these.
- When genuinely unsure, use SUSPICIOUS, never a false HIGH RISK.
Respond with JSON only, no prose."""


def _llm_classify(report: Report) -> Classification:
    data = chat_json(SYSTEM_PROMPT, f"Citizen received:\n\"\"\"\n{report.raw_text}\n\"\"\"")
    verdict = data.get("verdict", "SUSPICIOUS")
    if verdict not in ("HIGH RISK", "SUSPICIOUS", "LIKELY SAFE"):
        verdict = "SUSPICIOUS"
    msid = data.get("matched_script_id")
    if msid not in SCRIPTS_BY_ID:
        msid = None
    return Classification(
        verdict=verdict,
        scam_type=str(data.get("scam_type", "Unknown")),
        confidence=float(data.get("confidence", 0.5)),
        red_flags=[str(f) for f in data.get("red_flags", []) if f],
        advice=str(data.get("advice", "")) or rules.DEFAULT_ADVICE[verdict],
        matched_script_id=msid,
    )


def classify(report: Report) -> Classification:
    """LLM verdict + rule adjustment, with rules-only fallback."""
    try:
        llm = _llm_classify(report)
        return rules.adjust(llm, report)
    except LLMUnavailable:
        log.info("Classifying with rules only (LLM unavailable).")
        return rules.rules_only_classification(report)


def apply_to(report: Report) -> Report:
    """Run classify and merge the verdict block back onto the report, localizing
    the advice into the requested language (Component 5)."""
    from data.i18n import advice_for

    c = classify(report)
    report.verdict = c.verdict
    report.scam_type = c.scam_type
    report.confidence = c.confidence
    report.red_flags = c.red_flags
    report.matched_script_id = c.matched_script_id
    # localized advice for the chosen language; English keeps the LLM/rule advice.
    lang = report.language or "en"
    report.advice = c.advice if lang == "en" else (advice_for(c.verdict, lang) or c.advice)
    return report

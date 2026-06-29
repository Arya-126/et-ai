"""Agentic scam-baiting honeypot + IoC sinkholing.

A local-LLM agent poses as a confused, vulnerable victim to keep a flagged scammer
on the line — wasting their operational time while extracting indicators of
compromise (payment-drop UPI handles / mule accounts / phone numbers / domains).
Extracted IoCs are then *sinkholed*: propagated (simulated) to telecom + banking
APIs and added to the live block-list so the infrastructure is burned in real time.

The agent never reveals real personal or financial data. LLM via Ollama with a
deterministic fallback so it works offline.
"""
from __future__ import annotations

import re

from app.llm import LLMUnavailable, chat_json

IOC_PATTERNS = {
    "upi": re.compile(r"\b([a-z0-9._-]{2,}@[a-z]{2,})\b", re.I),
    "account": re.compile(r"\b(\d{11,18})\b"),
    "phone": re.compile(r"(?:\+?91[\-\s]?)?\b([6-9]\d{9})\b"),
    "url": re.compile(r"\b((?:https?://)?[a-z0-9-]+\.(?:com|in|net|org|xyz|info|link)[^\s]*)\b", re.I),
}

SYSTEM = (
    "You are an undercover anti-fraud honeypot. You pose as 'Kamala', a confused, "
    "polite 68-year-old who is scared but cooperative, to keep a scammer talking and "
    "reveal their payment details. NEVER reveal real OTPs, card numbers, or personal "
    "data. Stall: act a little confused, say the app is loading, and ASK THEM TO REPEAT "
    "the exact UPI id / account number / amount so they say it again. Stay in character. "
    'Return STRICT JSON: {"reply": "<what Kamala says next>", '
    '"observed_tactics": ["short notes on the scammer tactics"]}'
)


def extract_iocs(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for kind, pat in IOC_PATTERNS.items():
        vals = sorted({m.group(1) for m in pat.finditer(text or "")})
        # avoid double-counting a UPI's left part as a phone/account
        if kind == "phone":
            vals = [v for v in vals if f"{v}@" not in (text or "")]
        if vals:
            out[kind] = vals
    return out


_FALLBACK_REPLIES = [
    "Oh dear, sorry beta, the app is loading slowly… can you tell me the UPI id once more, slowly?",
    "I am very scared. Please repeat the account number, my eyes are weak and I want to write it correctly.",
    "Wait, my phone is hanging. What amount did you say, and to which UPI should I send it?",
    "I don't understand these things… can you say the full account number again so my son can check?",
]


def engage(history: list[dict], scammer_message: str) -> dict:
    """Generate the honeypot's next stalling reply and extract IoCs from the
    scammer's message. history = [{role, content}, ...]."""
    iocs = extract_iocs(scammer_message)
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in (history or []))
    user = f"Conversation so far:\n{convo}\nScammer just said: \"{scammer_message}\"\nReply as Kamala."

    reply, tactics = None, []
    try:
        data = chat_json(SYSTEM, user)
        reply = str(data.get("reply") or "").strip() or None
        tactics = [str(t) for t in data.get("observed_tactics", []) if t][:4]
    except LLMUnavailable:
        pass
    if not reply:
        reply = _FALLBACK_REPLIES[len(history or []) % len(_FALLBACK_REPLIES)]

    return {
        "reply": reply,
        "observed_tactics": tactics,
        "extracted_iocs": iocs,
        "time_wasted_seconds": 35 * (len(history or []) + 1),   # cumulative stall time
    }


# --- sinkhole store -------------------------------------------------------
class SinkholeStore:
    def __init__(self) -> None:
        self._iocs: dict[str, dict] = {}   # value -> record

    def push(self, iocs: dict[str, list[str]]) -> list[dict]:
        targets = {"upi": "NPCI / bank UPI block API", "account": "Bank mule-account freeze API",
                   "phone": "Telecom block/monitor API", "url": "DNS/registrar takedown + sinkhole"}
        added = []
        for kind, vals in (iocs or {}).items():
            for v in vals:
                rec = {"ioc": v, "kind": kind, "propagated_to": targets.get(kind, "—"),
                       "status": "sinkholed"}
                self._iocs[v] = rec
                added.append(rec)
        return added

    def all(self) -> list[dict]:
        return list(self._iocs.values())

    def reset(self) -> None:
        self._iocs.clear()


sinkhole_store = SinkholeStore()


def sinkhole(iocs: dict[str, list[str]]) -> dict:
    propagated = sinkhole_store.push(iocs)
    return {"propagated": propagated, "total_sinkholed": len(sinkhole_store.all())}

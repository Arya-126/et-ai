"""THE LOCK. Everything codes against these models. Change only by team agreement.

Report flows: IntakeAgent fills the raw/entity fields, ClassifierAgent fills the
verdict block, GraphLinkerAgent reads it all to write nodes/edges.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field

Channel = Literal["call", "sms", "whatsapp", "email", "screenshot"]
Verdict = Literal["HIGH RISK", "SUSPICIOUS", "LIKELY SAFE"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


class Report(BaseModel):
    """A single citizen report. The atomic unit of the whole system."""

    report_id: str = Field(default_factory=_new_id)
    raw_text: str
    channel: Channel = "whatsapp"

    # --- entities (filled by IntakeAgent) ---
    claimed_authority: Optional[str] = None  # "CBI", "TRAI", "Customs", "bank", ...
    phone: Optional[str] = None              # E.164-ish normalized
    upi_id: Optional[str] = None             # name@bank
    account_no: Optional[str] = None
    device_hint: Optional[str] = None        # device fingerprint / IMEI stub
    reporter_id: Optional[str] = None        # victim pseudo-id
    district: Optional[str] = None
    timestamp: datetime = Field(default_factory=_now)

    # --- digital-arrest / call metadata (optional signals) ---
    video_call: Optional[bool] = None        # scammer demanded a video call
    caller_spoofed: Optional[bool] = None     # caller ID looks spoofed
    caller_is_known: Optional[bool] = None    # False = unsaved number (Call Guard)

    # --- verdict block (filled by ClassifierAgent) ---
    verdict: Optional[Verdict] = None
    scam_type: Optional[str] = None
    confidence: Optional[float] = None
    red_flags: list[str] = Field(default_factory=list)
    advice: Optional[str] = None
    matched_script_id: Optional[str] = None
    language: str = "en"                       # localized advice language

    # --- alerting (filled by AlertingAgent on HIGH RISK digital-arrest) ---
    alert: Optional["Alert"] = None


class ReportInput(BaseModel):
    """What the citizen app POSTs. Just the raw paste + channel hint."""

    raw_text: str
    channel: Channel = "whatsapp"
    reporter_id: Optional[str] = None
    district: Optional[str] = None
    language: str = "en"                       # ISO code; localizes the verdict/advice
    phone: Optional[str] = None                # caller number (Call Guard)
    caller_is_known: Optional[bool] = None     # False = unsaved number (Call Guard)


class Classification(BaseModel):
    """ClassifierAgent output, merged back into the Report."""

    verdict: Verdict
    scam_type: str
    confidence: float
    red_flags: list[str] = Field(default_factory=list)
    advice: str
    matched_script_id: Optional[str] = None


# --------------------------------------------------------------------------
# Graph DTOs — what GraphStore implementations return. Frontends + PDF consume
# these and never touch Neo4j/NetworkX directly.
# --------------------------------------------------------------------------

class GraphNode(BaseModel):
    id: str                       # stable id, e.g. "UPI:fraud@okaxis"
    label: str                    # node type: Report, UPI, Account, ...
    value: str                    # display value
    community: Optional[int] = None
    is_kingpin: bool = False
    size: float = 1.0             # for viz weighting (e.g. degree)


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str                     # USED_NUMBER, PAID_TO, ...


class GraphDTO(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class ScoredNode(BaseModel):
    id: str
    label: str
    value: str
    score: float


class Ring(BaseModel):
    ring_id: str                  # e.g. "ring-3" (community id based)
    community: int
    size: int                     # number of nodes
    report_count: int
    districts: list[str] = Field(default_factory=list)
    states: list[str] = Field(default_factory=list)   # cross-jurisdiction framing
    node_ids: list[str] = Field(default_factory=list)
    top_node: Optional[ScoredNode] = None   # the kingpin (highest PageRank)


# --------------------------------------------------------------------------
# Component 1 — Digital Arrest alerting
# --------------------------------------------------------------------------

AlertKind = Literal["MHA", "TELECOM", "CONTACT"]


class Alert(BaseModel):
    alert_id: str = Field(default_factory=_new_id)
    report_id: str
    kind: AlertKind                # MHA/I4C escalation or telecom block/monitor
    target: str                    # who it goes to (e.g. "I4C / MHA", "Telecom: Airtel")
    summary: str
    scam_type: Optional[str] = None
    phone: Optional[str] = None
    upi_id: Optional[str] = None
    district: Optional[str] = None
    created: datetime = Field(default_factory=_now)


# --------------------------------------------------------------------------
# Component 2 — Counterfeit currency CV
# --------------------------------------------------------------------------

class CurrencyFeature(BaseModel):
    name: str                      # "Microprint", "Security thread", ...
    passed: bool
    detail: str
    score: float                   # 0..1


class CurrencyResult(BaseModel):
    verdict: Literal["GENUINE", "COUNTERFEIT", "UNCERTAIN"]
    confidence: float
    denomination: Optional[str] = None     # "₹500", ...
    features: list[CurrencyFeature] = Field(default_factory=list)
    model: str = "note-cnn"                # which model produced the verdict


# --------------------------------------------------------------------------
# Component 4 — Geospatial
# --------------------------------------------------------------------------

class GeoPoint(BaseModel):
    district: str
    state: str
    lat: float
    lng: float
    count: int = 1
    high_risk: int = 0
    kind: str = "complaint"        # complaint | seizure | hotspot


class GeoDTO(BaseModel):
    points: list[GeoPoint] = Field(default_factory=list)        # individual complaints
    hotspots: list[GeoPoint] = Field(default_factory=list)      # aggregated per district
    seizures: list[GeoPoint] = Field(default_factory=list)      # counterfeit seizures
    patrol_priority: list[GeoPoint] = Field(default_factory=list)  # ranked districts


# --------------------------------------------------------------------------
# Call Guard — phone-call screening + number reputation
# --------------------------------------------------------------------------

class CallInput(BaseModel):
    """What the Call Guard screens: a (possibly unsaved) caller + transcript."""
    caller_number: str
    is_saved: bool = False                     # is the number in the user's contacts?
    transcript: str                            # what the caller said (ASR or typed)
    video_call: bool = False
    language: str = "en"
    district: Optional[str] = None


class NumberReputation(BaseModel):
    phone: str
    known: bool = False                        # seen before in the fraud graph
    report_count: int = 0
    in_ring: bool = False
    ring_id: Optional[str] = None
    scam_types: list[str] = Field(default_factory=list)


class CallScreenResult(BaseModel):
    report: Report                             # the classified call
    reputation: NumberReputation


# Resolve the Report.alert forward reference now that Alert is defined.
Report.model_rebuild()

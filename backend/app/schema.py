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

    # --- verdict block (filled by ClassifierAgent) ---
    verdict: Optional[Verdict] = None
    scam_type: Optional[str] = None
    confidence: Optional[float] = None
    red_flags: list[str] = Field(default_factory=list)
    advice: Optional[str] = None
    matched_script_id: Optional[str] = None


class ReportInput(BaseModel):
    """What the citizen app POSTs. Just the raw paste + channel hint."""

    raw_text: str
    channel: Channel = "whatsapp"
    reporter_id: Optional[str] = None
    district: Optional[str] = None


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
    node_ids: list[str] = Field(default_factory=list)
    top_node: Optional[ScoredNode] = None   # the kingpin (highest PageRank)

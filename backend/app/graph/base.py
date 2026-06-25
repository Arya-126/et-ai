"""The GraphStore seam. Neo4j and NetworkX both implement this ABC, returning
identical DTOs so the rest of the system (routers, PDF, frontends) never cares
which engine is live.

Node id convention: "<Label>:<value>" — e.g. "UPI:fraud@okaxis", "Report:ab12cd".
This makes MERGE/dedup trivial and keeps ids stable across writes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.schema import GraphDTO, Report, Ring, ScoredNode


def node_id(label: str, value: str) -> str:
    return f"{label}:{value}"


class GraphStore(ABC):
    """Write reports in, get rings/centrality/subgraphs out."""

    @abstractmethod
    def write_report(self, r: Report) -> None:
        """MERGE the report and all its entities (phone/upi/account/device/
        script/reporter/district) plus the edges between them. Idempotent."""

    @abstractmethod
    def get_graph(self) -> GraphDTO:
        """The whole graph with community ids attached to nodes (run Louvain
        lazily if needed). Used by GET /graph for the force-directed viz."""

    @abstractmethod
    def detect_rings(self) -> list[Ring]:
        """Louvain communities with size >= settings.min_ring_size, enriched
        with report counts, districts, and the top-PageRank node (kingpin)."""

    @abstractmethod
    def centrality(self, ring_id: str) -> list[ScoredNode]:
        """PageRank over the ring's subgraph, restricted to Account/PhoneNumber/
        UPI nodes (the actionable infrastructure). Descending score."""

    @abstractmethod
    def subgraph(self, ring_id: str) -> GraphDTO:
        """Just one ring's nodes + edges, for the intelligence package."""

    @abstractmethod
    def district_stats(self) -> dict[str, dict]:
        """Per-district aggregates for the geospatial layer:
        {district: {"total": int, "high_risk": int}}."""

    @abstractmethod
    def reset(self) -> None:
        """Wipe the graph (used by seed.py for a clean reload)."""

    def close(self) -> None:  # optional override
        pass

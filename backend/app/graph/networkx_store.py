"""In-memory NetworkX fallback. Zero infra, always works — the live-demo
insurance. Implements the exact same GraphStore contract as Neo4j.

Rings come from python-louvain (community.best_partition); the kingpin comes
from networkx PageRank restricted to actionable infrastructure nodes.
"""
from __future__ import annotations

import networkx as nx

try:
    import community as community_louvain  # python-louvain
except ImportError:  # pragma: no cover
    community_louvain = None

from app.config import settings
from app.graph.base import GraphStore
from app.graph.entities import nid, report_graph
from app.schema import GraphDTO, GraphEdge, GraphNode, Report, Ring, ScoredNode

# Nodes that represent actionable fraud infrastructure (the things you'd act on).
ACTIONABLE = {"Account", "PhoneNumber", "UPI"}


def _states_for(districts: list[str]) -> list[str]:
    from data.geo import state_of
    return sorted({s for d in districts if (s := state_of(d))})


class NetworkXStore(GraphStore):
    def __init__(self) -> None:
        self.g = nx.Graph()
        self._partition: dict[str, int] = {}

    # ---- writes -------------------------------------------------------------
    def write_report(self, r: Report) -> None:
        nodes, edges = report_graph(r)
        for label, value in nodes:
            n = nid(label, value)
            if not self.g.has_node(n):
                self.g.add_node(n, label=label, value=value)
        # district / verdict ride as attributes on the Report node (not edges)
        rnode = nid("Report", r.report_id)
        self.g.nodes[rnode]["district"] = r.district
        self.g.nodes[rnode]["verdict"] = r.verdict
        for s_label, s_val, etype, d_label, d_val in edges:
            self.g.add_edge(
                nid(s_label, s_val), nid(d_label, d_val), type=etype
            )
        self._partition = {}  # invalidate cached communities

    def reset(self) -> None:
        self.g = nx.Graph()
        self._partition = {}

    def district_stats(self) -> dict[str, dict]:
        stats: dict[str, dict] = {}
        for n, d in self.g.nodes(data=True):
            if d.get("label") != "Report":
                continue
            district = d.get("district")
            if not district:
                continue
            s = stats.setdefault(district, {"total": 0, "high_risk": 0})
            s["total"] += 1
            if d.get("verdict") == "HIGH RISK":
                s["high_risk"] += 1
        return stats

    # ---- community detection (Louvain) -------------------------------------
    def _partition_graph(self) -> dict[str, int]:
        if self._partition:
            return self._partition
        if self.g.number_of_nodes() == 0:
            return {}
        if community_louvain is not None:
            self._partition = community_louvain.best_partition(self.g, random_state=42)
        else:  # graceful degrade: connected components as "communities"
            self._partition = {}
            for i, comp in enumerate(nx.connected_components(self.g)):
                for n in comp:
                    self._partition[n] = i
        return self._partition

    def _ring_nodes(self, community: int) -> list[str]:
        part = self._partition_graph()
        return [n for n, c in part.items() if c == community]

    def _pagerank_in(self, node_ids: list[str]) -> dict[str, float]:
        sub = self.g.subgraph(node_ids)
        if sub.number_of_nodes() == 0:
            return {}
        return nx.pagerank(sub, alpha=0.85)

    def _kingpin(self, node_ids: list[str]) -> ScoredNode | None:
        pr = self._pagerank_in(node_ids)
        best, best_score = None, -1.0
        for n, score in pr.items():
            if self.g.nodes[n].get("label") in ACTIONABLE and score > best_score:
                best, best_score = n, score
        if best is None:
            return None
        d = self.g.nodes[best]
        return ScoredNode(id=best, label=d["label"], value=d["value"], score=round(best_score, 4))

    # ---- reads --------------------------------------------------------------
    def get_graph(self) -> GraphDTO:
        part = self._partition_graph()
        rings = {r.community for r in self.detect_rings()}
        kingpins = {r.top_node.id for r in self.detect_rings() if r.top_node}
        nodes = [
            GraphNode(
                id=n,
                label=d["label"],
                value=d["value"],
                community=part.get(n),
                is_kingpin=n in kingpins,
                size=1.0 + self.g.degree(n),
            )
            for n, d in self.g.nodes(data=True)
        ]
        edges = [
            GraphEdge(source=u, target=v, type=d.get("type", "LINK"))
            for u, v, d in self.g.edges(data=True)
        ]
        # only color nodes that belong to an actual ring; isolate noise as community None
        for node in nodes:
            if node.community not in rings:
                node.community = None
        return GraphDTO(nodes=nodes, edges=edges)

    def detect_rings(self) -> list[Ring]:
        part = self._partition_graph()
        by_comm: dict[int, list[str]] = {}
        for n, c in part.items():
            by_comm.setdefault(c, []).append(n)

        rings: list[Ring] = []
        for comm, members in by_comm.items():
            if len(members) < settings.min_ring_size:
                continue
            reports = [n for n in members if self.g.nodes[n]["label"] == "Report"]
            districts = sorted(
                {self.g.nodes[n].get("district") for n in reports if self.g.nodes[n].get("district")}
            )
            rings.append(
                Ring(
                    ring_id=f"ring-{comm}",
                    community=comm,
                    size=len(members),
                    report_count=len(reports),
                    districts=districts,
                    states=_states_for(districts),
                    node_ids=members,
                    top_node=self._kingpin(members),
                )
            )
        rings.sort(key=lambda r: r.report_count, reverse=True)
        return rings

    def centrality(self, ring_id: str) -> list[ScoredNode]:
        comm = int(ring_id.split("-")[-1])
        members = self._ring_nodes(comm)
        pr = self._pagerank_in(members)
        scored = [
            ScoredNode(
                id=n,
                label=self.g.nodes[n]["label"],
                value=self.g.nodes[n]["value"],
                score=round(s, 4),
            )
            for n, s in pr.items()
            if self.g.nodes[n]["label"] in ACTIONABLE
        ]
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored

    def subgraph(self, ring_id: str) -> GraphDTO:
        comm = int(ring_id.split("-")[-1])
        members = self._ring_nodes(comm)
        member_set = set(members)
        kingpin = self._kingpin(members)
        nodes = [
            GraphNode(
                id=n,
                label=self.g.nodes[n]["label"],
                value=self.g.nodes[n]["value"],
                community=comm,
                is_kingpin=bool(kingpin and kingpin.id == n),
                size=1.0 + self.g.degree(n),
            )
            for n in members
        ]
        edges = [
            GraphEdge(source=u, target=v, type=d.get("type", "LINK"))
            for u, v, d in self.g.edges(data=True)
            if u in member_set and v in member_set
        ]
        return GraphDTO(nodes=nodes, edges=edges)

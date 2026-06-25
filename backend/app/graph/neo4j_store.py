"""Neo4j + Graph Data Science store — the primary, "real graph DB" path and the
technical showpiece. MERGE writes; GDS Louvain for rings; GDS PageRank for the
kingpin.

Read methods pull the graph + GDS scores into memory and assemble the same DTOs
the NetworkX store produces, so the two backends are interchangeable.

Node model: every node carries `id` ("Label:value") and `value`. Its Neo4j
label is one of the fixed taxonomy labels (Report, UPI, Account, ...).
"""
from __future__ import annotations

from neo4j import GraphDatabase

from app.config import settings
from app.graph.base import GraphStore
from app.graph.entities import nid, report_graph
from app.schema import GraphDTO, GraphEdge, GraphNode, Report, Ring, ScoredNode

ACTIONABLE = {"Account", "PhoneNumber", "UPI"}
GRAPH_NAME = "fraudGraph"


class Neo4jStore(GraphStore):
    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )
        self.driver.verify_connectivity()  # raises if Neo4j is unreachable
        self._ensure_constraints()

    def close(self) -> None:
        self.driver.close()

    def _ensure_constraints(self) -> None:
        labels = ["Report", "PhoneNumber", "UPI", "Account", "Device",
                  "ScamScript", "Reporter"]
        with self.driver.session() as s:
            for label in labels:
                s.run(
                    f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS "
                    f"FOR (n:{label}) REQUIRE n.id IS UNIQUE"
                )

    # ---- writes -------------------------------------------------------------
    def write_report(self, r: Report) -> None:
        nodes, edges = report_graph(r)
        with self.driver.session() as s:
            for label, value in nodes:
                s.run(
                    f"MERGE (n:{label} {{id: $id}}) SET n.value = $value",
                    id=nid(label, value), value=value,
                )
            # district / verdict as attributes on the Report node (not edges)
            s.run(
                "MATCH (n:Report {id:$id}) SET n.district = $district, n.verdict = $verdict",
                id=nid("Report", r.report_id), district=r.district, verdict=r.verdict,
            )
            for s_label, s_val, etype, d_label, d_val in edges:
                s.run(
                    f"MATCH (a:{s_label} {{id:$sid}}), (b:{d_label} {{id:$did}}) "
                    f"MERGE (a)-[:{etype}]->(b)",
                    sid=nid(s_label, s_val), did=nid(d_label, d_val),
                )

    def reset(self) -> None:
        with self.driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")

    # ---- GDS compute --------------------------------------------------------
    def _project(self, session) -> None:
        session.run(
            "CALL gds.graph.exists($g) YIELD exists "
            "WITH exists WHERE exists CALL gds.graph.drop($g) YIELD graphName "
            "RETURN graphName", g=GRAPH_NAME,
        )
        session.run(
            "CALL gds.graph.project($g, '*', "
            "{ALL: {type: '*', orientation: 'UNDIRECTED'}}) "
            "YIELD graphName RETURN graphName", g=GRAPH_NAME,
        )

    def _compute(self):
        """Return (nodes_meta, edges, partition, pagerank)."""
        with self.driver.session() as s:
            nodes_meta = {
                rec["id"]: {"label": rec["label"], "value": rec["value"],
                            "degree": rec["degree"], "district": rec["district"]}
                for rec in s.run(
                    "MATCH (n) RETURN n.id AS id, head(labels(n)) AS label, "
                    "n.value AS value, n.district AS district, COUNT{(n)--()} AS degree"
                )
            }
            edges = [
                (rec["a"], rec["b"], rec["t"])
                for rec in s.run(
                    "MATCH (a)-[e]->(b) RETURN a.id AS a, b.id AS b, type(e) AS t"
                )
            ]
            partition, pagerank = {}, {}
            if nodes_meta:
                self._project(s)
                for rec in s.run(
                    "CALL gds.louvain.stream($g) YIELD nodeId, communityId "
                    "RETURN gds.util.asNode(nodeId).id AS id, communityId AS c",
                    g=GRAPH_NAME,
                ):
                    partition[rec["id"]] = rec["c"]
                for rec in s.run(
                    "CALL gds.pageRank.stream($g) YIELD nodeId, score "
                    "RETURN gds.util.asNode(nodeId).id AS id, score AS s",
                    g=GRAPH_NAME,
                ):
                    pagerank[rec["id"]] = rec["s"]
        return nodes_meta, edges, partition, pagerank

    @staticmethod
    def _kingpin(member_ids, nodes_meta, pagerank) -> ScoredNode | None:
        best, best_score = None, -1.0
        for n in member_ids:
            meta = nodes_meta.get(n, {})
            if meta.get("label") in ACTIONABLE and pagerank.get(n, 0) > best_score:
                best, best_score = n, pagerank.get(n, 0)
        if best is None:
            return None
        m = nodes_meta[best]
        return ScoredNode(id=best, label=m["label"], value=m["value"],
                          score=round(best_score, 4))

    def _rings_from(self, nodes_meta, partition, pagerank) -> list[Ring]:
        by_comm: dict[int, list[str]] = {}
        for n, c in partition.items():
            by_comm.setdefault(c, []).append(n)
        rings = []
        for comm, members in by_comm.items():
            if len(members) < settings.min_ring_size:
                continue
            reports = [n for n in members if nodes_meta[n]["label"] == "Report"]
            districts = sorted(
                {nodes_meta[n].get("district") for n in reports if nodes_meta[n].get("district")}
            )
            rings.append(Ring(
                ring_id=f"ring-{comm}", community=comm, size=len(members),
                report_count=len(reports), districts=districts, node_ids=members,
                top_node=self._kingpin(members, nodes_meta, pagerank),
            ))
        rings.sort(key=lambda r: r.report_count, reverse=True)
        return rings

    # ---- reads --------------------------------------------------------------
    def detect_rings(self) -> list[Ring]:
        nodes_meta, _edges, partition, pagerank = self._compute()
        return self._rings_from(nodes_meta, partition, pagerank)

    def get_graph(self) -> GraphDTO:
        nodes_meta, edges, partition, pagerank = self._compute()
        rings = self._rings_from(nodes_meta, partition, pagerank)
        ring_comms = {r.community for r in rings}
        kingpins = {r.top_node.id for r in rings if r.top_node}
        nodes = [
            GraphNode(
                id=n, label=m["label"], value=m["value"],
                community=partition.get(n) if partition.get(n) in ring_comms else None,
                is_kingpin=n in kingpins, size=1.0 + m["degree"],
            )
            for n, m in nodes_meta.items()
        ]
        return GraphDTO(
            nodes=nodes,
            edges=[GraphEdge(source=a, target=b, type=t) for a, b, t in edges],
        )

    def centrality(self, ring_id: str) -> list[ScoredNode]:
        comm = int(ring_id.split("-")[-1])
        nodes_meta, _edges, partition, pagerank = self._compute()
        members = [n for n, c in partition.items() if c == comm]
        scored = [
            ScoredNode(id=n, label=nodes_meta[n]["label"],
                       value=nodes_meta[n]["value"], score=round(pagerank.get(n, 0), 4))
            for n in members if nodes_meta[n]["label"] in ACTIONABLE
        ]
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored

    def subgraph(self, ring_id: str) -> GraphDTO:
        comm = int(ring_id.split("-")[-1])
        nodes_meta, edges, partition, pagerank = self._compute()
        members = {n for n, c in partition.items() if c == comm}
        kingpin = self._kingpin(list(members), nodes_meta, pagerank)
        nodes = [
            GraphNode(
                id=n, label=nodes_meta[n]["label"], value=nodes_meta[n]["value"],
                community=comm, is_kingpin=bool(kingpin and kingpin.id == n),
                size=1.0 + nodes_meta[n]["degree"],
            )
            for n in members
        ]
        return GraphDTO(
            nodes=nodes,
            edges=[GraphEdge(source=a, target=b, type=t)
                   for a, b, t in edges if a in members and b in members],
        )

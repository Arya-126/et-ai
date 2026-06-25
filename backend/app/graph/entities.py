"""Single source of truth for turning a Report into graph nodes + edges.
Both Neo4j and NetworkX stores call this so the taxonomy can never drift.
"""
from __future__ import annotations

from app.graph.base import node_id
from app.schema import Report

# (label, value) tuples
NodeSpec = tuple[str, str]
# (src_label, src_value, edge_type, dst_label, dst_value)
EdgeSpec = tuple[str, str, str, str, str]


def report_graph(r: Report) -> tuple[list[NodeSpec], list[EdgeSpec]]:
    """Return the nodes and edges a single report contributes to the graph."""
    nodes: list[NodeSpec] = [("Report", r.report_id)]
    edges: list[EdgeSpec] = []

    def link(edge_type: str, label: str, value: str | None) -> None:
        if not value:
            return
        nodes.append((label, value))
        edges.append(("Report", r.report_id, edge_type, label, value))

    link("REPORTED_BY", "Reporter", r.reporter_id)
    link("USED_NUMBER", "PhoneNumber", r.phone)
    link("PAID_TO", "UPI", r.upi_id)
    link("PAID_TO", "Account", r.account_no)
    link("FROM_DEVICE", "Device", r.device_hint)
    link("MATCHES_SCRIPT", "ScamScript", r.matched_script_id)
    # NOTE: District is deliberately NOT a connecting node — it is a high-degree
    # hub that would cluster every unrelated report in the same city into a false
    # ring. District is carried as an attribute on the Report node instead.

    return nodes, edges


def nid(label: str, value: str) -> str:
    return node_id(label, value)

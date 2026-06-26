"""Number reputation — the Call Guard's tie-in to the fraud graph. A caller number
already seen in prior reports (or sitting inside a detected ring) is a known scammer,
so we can flag the call HIGH RISK before a single word of the transcript is parsed.

Derived from the live GraphStore via get_graph()/detect_rings() — no ABC change.
"""
from __future__ import annotations

from app.graph.base import node_id
from app.graph.factory import get_store
from app.schema import GraphDTO, NumberReputation
from data.scam_scripts import SCRIPTS_BY_ID


def _adjacency(graph: GraphDTO) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {}
    for e in graph.edges:
        adj.setdefault(e.source, []).append(e.target)
        adj.setdefault(e.target, []).append(e.source)
    return adj


def lookup(phone: str) -> NumberReputation:
    if not phone:
        return NumberReputation(phone=phone or "", known=False)
    store = get_store()
    graph = store.get_graph()
    nodes_by_id = {n.id: n for n in graph.nodes}
    pid = node_id("PhoneNumber", phone)
    if pid not in nodes_by_id:
        return NumberReputation(phone=phone, known=False)

    adj = _adjacency(graph)
    report_ids = [n for n in adj.get(pid, [])
                  if (m := nodes_by_id.get(n)) and m.label == "Report"]
    scam_types: set[str] = set()
    for rid in report_ids:
        for nb in adj.get(rid, []):
            m = nodes_by_id.get(nb)
            if m and m.label == "ScamScript":
                s = SCRIPTS_BY_ID.get(m.value)
                scam_types.add(s.family if s else m.value)

    in_ring, ring_id = False, None
    for ring in store.detect_rings():
        if pid in ring.node_ids:
            in_ring, ring_id = True, ring.ring_id
            break

    return NumberReputation(
        phone=phone, known=len(report_ids) > 0, report_count=len(report_ids),
        in_ring=in_ring, ring_id=ring_id, scam_types=sorted(scam_types),
    )


def blocklist(min_reports: int = 3, limit: int = 25) -> list[NumberReputation]:
    """Known scammer numbers mined from the graph: phones in a ring, or seen in
    >= min_reports reports."""
    store = get_store()
    graph = store.get_graph()
    nodes_by_id = {n.id: n for n in graph.nodes}
    adj = _adjacency(graph)
    ring_nodes: set[str] = set()
    for ring in store.detect_rings():
        ring_nodes.update(ring.node_ids)

    out: list[NumberReputation] = []
    for n in graph.nodes:
        if n.label != "PhoneNumber":
            continue
        reports = [x for x in adj.get(n.id, [])
                   if (m := nodes_by_id.get(x)) and m.label == "Report"]
        if len(reports) >= min_reports or n.id in ring_nodes:
            out.append(NumberReputation(
                phone=n.value, known=True, report_count=len(reports),
                in_ring=n.id in ring_nodes,
            ))
    out.sort(key=lambda r: (r.in_ring, r.report_count), reverse=True)
    return out[:limit]

"""PackageAgent — on-demand from the LE dashboard. Runs GDS (via the store),
pulls one ring's subgraph + centrality, and renders the court-ready PDF.
"""
from __future__ import annotations

from app.graph.factory import get_store
from app.reporting.pdf import build_package_pdf
from app.schema import GraphDTO, Ring, ScoredNode


class IntelligencePackage:
    def __init__(self, ring: Ring, subgraph: GraphDTO, centrality: list[ScoredNode], pdf_path: str):
        self.ring = ring
        self.subgraph = subgraph
        self.centrality = centrality
        self.pdf_path = pdf_path


def _find_ring(ring_id: str) -> Ring | None:
    for r in get_store().detect_rings():
        if r.ring_id == ring_id:
            return r
    return None


def build(ring_id: str) -> IntelligencePackage | None:
    store = get_store()
    ring = _find_ring(ring_id)
    if ring is None:
        return None
    sub = store.subgraph(ring_id)
    cent = store.centrality(ring_id)
    pdf_path = build_package_pdf(ring, sub, cent)
    return IntelligencePackage(ring, sub, cent, pdf_path)

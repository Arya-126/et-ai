"""Picks the graph backend and — critically — auto-falls-back to NetworkX if
Neo4j is selected but unreachable. The whole demo's resilience lives here:
one call, one global store, never a hard failure on stage.
"""
from __future__ import annotations

import logging

from app.config import settings
from app.graph.base import GraphStore
from app.graph.networkx_store import NetworkXStore

log = logging.getLogger("graph.factory")

_store: GraphStore | None = None


def _build() -> GraphStore:
    if settings.graph_backend == "networkx":
        log.info("Graph backend: NetworkX (configured).")
        return NetworkXStore()

    # Try Neo4j, fall back to NetworkX on any connection problem.
    try:
        from app.graph.neo4j_store import Neo4jStore

        store = Neo4jStore()
        log.info("Graph backend: Neo4j + GDS.")
        return store
    except Exception as exc:  # noqa: BLE001 — demo insurance, catch everything
        log.warning(
            "Neo4j unavailable (%s). Falling back to NetworkX — demo continues.", exc
        )
        return NetworkXStore()


def get_store() -> GraphStore:
    global _store
    if _store is None:
        _store = _build()
    return _store


def reset_store() -> None:
    """For tests / re-seeding within one process."""
    global _store
    if _store is not None:
        _store.close()
    _store = None

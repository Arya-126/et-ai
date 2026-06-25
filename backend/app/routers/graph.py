"""GET /graph — full graph + community colors for the force-directed viz.
GET /rings — the detected rings (Detect Rings button)."""
from __future__ import annotations

from fastapi import APIRouter

from app.graph.factory import get_store
from app.schema import GraphDTO, Ring

router = APIRouter(tags=["intelligence"])


@router.get("/graph", response_model=GraphDTO)
def get_graph() -> GraphDTO:
    return get_store().get_graph()


@router.get("/rings", response_model=list[Ring])
def get_rings() -> list[Ring]:
    return get_store().detect_rings()

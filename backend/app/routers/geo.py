"""Geospatial Crime Pattern Intelligence (Component 4).
GET /geo -> complaint points, per-district hotspots, patrol-priority ranking,
            and counterfeit seizure points — for the Command-Centre map.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.geo_state import store as seizure_store
from app.graph.factory import get_store
from app.schema import GeoDTO, GeoPoint
from data.geo import DISTRICTS, latlng, state_of

router = APIRouter(tags=["geo"])


@router.get("/geo", response_model=GeoDTO)
def geo() -> GeoDTO:
    stats = get_store().district_stats()

    hotspots: list[GeoPoint] = []
    for district, s in stats.items():
        ll = latlng(district)
        if not ll:
            continue
        hotspots.append(GeoPoint(
            district=district, state=state_of(district) or "—",
            lat=ll[0], lng=ll[1], count=s["total"], high_risk=s["high_risk"],
            kind="hotspot",
        ))

    # complaint points = same coordinates (one marker per district carries its count)
    points = [p.model_copy(update={"kind": "complaint"}) for p in hotspots]

    # patrol priority: HIGH RISK count first, then total volume
    patrol = sorted(hotspots, key=lambda p: (p.high_risk, p.count), reverse=True)[:6]

    return GeoDTO(
        points=points,
        hotspots=hotspots,
        seizures=seizure_store.all(),
        patrol_priority=patrol,
    )

"""In-process store of counterfeit-currency seizure points for the geospatial
layer. Pre-seeded with a few demo seizures; the currency scanner appends a point
whenever it flags a COUNTERFEIT note (links Components 2 and 4).
"""
from __future__ import annotations

from data.geo import DISTRICTS, latlng
from app.schema import GeoPoint


class SeizureStore:
    def __init__(self) -> None:
        self._points: list[GeoPoint] = []
        self._seed()

    def _seed(self) -> None:
        for district in ("Delhi", "Mumbai", "Bengaluru"):
            ll = latlng(district)
            if ll:
                self._points.append(GeoPoint(
                    district=district, state=DISTRICTS[district][2],
                    lat=ll[0], lng=ll[1], count=1, kind="seizure"))

    def add(self, district: str) -> None:
        ll = latlng(district)
        if not ll or district not in DISTRICTS:
            return
        self._points.append(GeoPoint(
            district=district, state=DISTRICTS[district][2],
            lat=ll[0], lng=ll[1], count=1, kind="seizure"))

    def all(self) -> list[GeoPoint]:
        return list(self._points)


store = SeizureStore()

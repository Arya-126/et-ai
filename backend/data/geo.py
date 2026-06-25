"""District -> (lat, lng, state) lookup for every city the generator uses.
Powers the geospatial map and the cross-jurisdiction framing in rings/PDF.
Coordinates are approximate city centroids (public knowledge).
"""
from __future__ import annotations

# district: (lat, lng, state)
DISTRICTS: dict[str, tuple[float, float, str]] = {
    "Bengaluru": (12.9716, 77.5946, "Karnataka"),
    "Mysuru": (12.2958, 76.6394, "Karnataka"),
    "Mandya": (12.5223, 76.8954, "Karnataka"),
    "Delhi": (28.7041, 77.1025, "Delhi"),
    "Gurugram": (28.4595, 77.0266, "Haryana"),
    "Noida": (28.5355, 77.3910, "Uttar Pradesh"),
    "Mumbai": (19.0760, 72.8777, "Maharashtra"),
    "Pune": (18.5204, 73.8567, "Maharashtra"),
    "Thane": (19.2183, 72.9781, "Maharashtra"),
    "Chennai": (13.0827, 80.2707, "Tamil Nadu"),
    "Hyderabad": (17.3850, 78.4867, "Telangana"),
    "Kolkata": (22.5726, 88.3639, "West Bengal"),
    "Jaipur": (26.9124, 75.7873, "Rajasthan"),
    "Ahmedabad": (23.0225, 72.5714, "Gujarat"),
    "Lucknow": (26.8467, 80.9462, "Uttar Pradesh"),
    "Kochi": (9.9312, 76.2673, "Kerala"),
    "Bhopal": (23.2599, 77.4126, "Madhya Pradesh"),
    "Patna": (25.5941, 85.1376, "Bihar"),
    "Surat": (21.1702, 72.8311, "Gujarat"),
}


def latlng(district: str | None) -> tuple[float, float] | None:
    rec = DISTRICTS.get(district or "")
    return (rec[0], rec[1]) if rec else None


def state_of(district: str | None) -> str | None:
    rec = DISTRICTS.get(district or "")
    return rec[2] if rec else None

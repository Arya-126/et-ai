"""OpenCV per-feature explainability (Component 2). Inspects the regions where
genuine notes carry security features and reports a pass/score for each — this is
the breakdown shown next to the CNN verdict. Tuned to the synthetic note layout.
"""
from __future__ import annotations

import cv2
import numpy as np
from PIL import Image

from cv.generate_notes import MICRO_BOX, THREAD_X, UV_BOX, W, H
from app.schema import CurrencyFeature


def _resize(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGB").resize((W, H)))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def microprint(bgr: np.ndarray) -> CurrencyFeature:
    x0, y0, x1, y1 = MICRO_BOX
    region = cv2.cvtColor(bgr[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    sharp = cv2.Laplacian(region, cv2.CV_64F).var()       # crisp text => high variance
    score = float(min(sharp / 120.0, 1.0))
    return CurrencyFeature(name="Microprint", passed=sharp > 45,
                           detail=f"Laplacian sharpness {sharp:.0f}", score=round(score, 2))


def security_thread(bgr: np.ndarray) -> CurrencyFeature:
    band = cv2.cvtColor(bgr[:, THREAD_X - 6:THREAD_X + 12], cv2.COLOR_BGR2GRAY)
    darkness = 255.0 - float(band.mean())                 # thread is darker than bg
    score = float(min(darkness / 90.0, 1.0))
    return CurrencyFeature(name="Security thread", passed=darkness > 35,
                           detail=f"thread contrast {darkness:.0f}", score=round(score, 2))


def uv_patch(bgr: np.ndarray) -> CurrencyFeature:
    x0, y0, x1, y1 = UV_BOX
    region = bgr[y0:y1, x0:x1]
    b, g, r = region[..., 0].mean(), region[..., 1].mean(), region[..., 2].mean()
    cyan = (g + b) / 2 - r                                 # cyan patch => g,b high, r low
    score = float(min(max(cyan, 0) / 120.0, 1.0))
    return CurrencyFeature(name="UV feature", passed=cyan > 30,
                           detail=f"UV response {cyan:.0f}", score=round(score, 2))


def serial_pattern(bgr: np.ndarray) -> CurrencyFeature:
    # edge density in the serial region as a proxy for crisp, well-formed printing
    region = cv2.cvtColor(bgr[6:30, W - 155:W - 5], cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(region, 80, 160)
    density = float(edges.mean())
    score = float(min(density / 30.0, 1.0))
    return CurrencyFeature(name="Serial number", passed=density > 8,
                           detail=f"print clarity {density:.1f}", score=round(score, 2))


def extract(img: Image.Image) -> list[CurrencyFeature]:
    bgr = _resize(img)
    return [microprint(bgr), security_thread(bgr), uv_patch(bgr), serial_pattern(bgr)]


def guess_denomination(img: Image.Image) -> str:
    """Crude denomination guess from the dominant tint (synthetic notes are tinted)."""
    arr = np.asarray(img.convert("RGB").resize((W, H))).reshape(-1, 3).mean(0)
    r, g, b = arr
    if b > r and b > g:
        return "₹100"
    if r > 215 and g > 190 and b < 175:
        return "₹200"
    if r > 200 and b > 190 and g < 190:
        return "₹2000"
    return "₹500"

"""Counterfeit Currency Identification (Component 2).
POST /currency/scan        -> upload a note image, get verdict + feature breakdown
GET  /currency/samples     -> list demo sample notes
GET  /currency/samples/{id}-> the sample PNG
Deployable identically on mobile, POS, or bank-counting machines (same endpoint).
"""
from __future__ import annotations

import io
import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image

from app.geo_state import store as seizure_store
from app.schema import CurrencyResult
from cv import infer
from cv.generate_notes import ensure_samples

router = APIRouter(tags=["currency"])


@router.post("/currency/scan", response_model=CurrencyResult)
async def scan(file: UploadFile = File(...), district: str | None = Form(default=None)):
    try:
        img = Image.open(io.BytesIO(await file.read()))
    except Exception:
        raise HTTPException(400, "Could not read image")
    result = infer.scan(img)
    # link Components 2 -> 4: a flagged counterfeit becomes a seizure point
    if result.verdict == "COUNTERFEIT" and district:
        seizure_store.add(district)
    return result


@router.get("/currency/samples")
def samples():
    folder = ensure_samples()
    out = []
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".png"):
            continue
        sid = fn[:-4]
        label, denom = sid.split("_", 1)
        out.append({
            "id": sid,
            "expected": "COUNTERFEIT" if label == "fake" else "GENUINE",
            "denomination": f"₹{denom}",
            "url": f"/currency/samples/{sid}",
        })
    return out


@router.get("/currency/samples/{sid}")
def sample(sid: str):
    folder = ensure_samples()
    path = os.path.join(folder, f"{sid}.png")
    if not os.path.exists(path):
        raise HTTPException(404, "sample not found")
    return FileResponse(path, media_type="image/png")

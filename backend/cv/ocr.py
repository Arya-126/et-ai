"""Screenshot OCR (optional). Lazy easyocr (reuses the already-present torch). If
easyocr isn't installed or the model can't load, everything degrades gracefully —
extract_text returns None and the UI falls back to manual paste.

Install (optional):  pip install easyocr
"""
from __future__ import annotations

import io
import logging

log = logging.getLogger("cv.ocr")

_reader = None
_tried = False


def _get_reader():
    global _reader, _tried
    if _tried:
        return _reader
    _tried = True
    try:
        import easyocr  # noqa: PLC0415 — heavy optional import, kept lazy

        _reader = easyocr.Reader(["en"], gpu=False)
        log.info("easyocr ready.")
    except Exception as exc:  # noqa: BLE001 — easyocr/model/network absent
        log.info("OCR unavailable (%s); screenshot intake will ask the user to type.", exc)
    return _reader


def available() -> bool:
    return _get_reader() is not None


def extract_text(image_bytes: bytes) -> str | None:
    reader = _get_reader()
    if reader is None:
        return None
    try:
        import numpy as np
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        lines = reader.readtext(np.array(img), detail=0, paragraph=True)
        text = "\n".join(lines).strip()
        return text or None
    except Exception as exc:  # noqa: BLE001
        log.warning("OCR failed: %s", exc)
        return None

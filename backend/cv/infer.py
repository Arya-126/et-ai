"""Inference for the currency scanner (Component 2). Loads the CNN if trained and
combines its verdict with the OpenCV feature breakdown. If the model weights are
missing, degrades to a features-only verdict — so the endpoint always works
(same resilience pattern as the LLM/rules classifier).
"""
from __future__ import annotations

import logging
import os

import torch
from PIL import Image

from cv import features as feat
from cv.model import NoteCNN
from cv.preprocess import to_tensor
from app.schema import CurrencyResult

log = logging.getLogger("cv.infer")
WEIGHTS = os.path.join(os.path.dirname(__file__), "note_cnn.pt")

_model: NoteCNN | None = None
_loaded = False


def _get_model() -> NoteCNN | None:
    global _model, _loaded
    if _loaded:
        return _model
    _loaded = True
    if os.path.exists(WEIGHTS):
        try:
            m = NoteCNN()
            m.load_state_dict(torch.load(WEIGHTS, map_location="cpu"))
            m.eval()
            _model = m
            log.info("Loaded NoteCNN weights.")
        except Exception as exc:  # noqa: BLE001
            log.warning("Failed to load NoteCNN (%s); using features-only.", exc)
    else:
        log.info("No NoteCNN weights; using features-only verdict.")
    return _model


def scan(img: Image.Image) -> CurrencyResult:
    features = feat.extract(img)
    denom = feat.guess_denomination(img)
    feat_score = sum(f.score for f in features) / max(len(features), 1)  # 0..1 (1 = genuine-like)

    model = _get_model()
    if model is not None:
        with torch.no_grad():
            probs = torch.softmax(model(to_tensor(img).unsqueeze(0)), dim=1)[0]
        p_fake = float(probs[1])
        # blend CNN with the explainable feature score (low feat_score => fake-ish)
        fake_conf = 0.7 * p_fake + 0.3 * (1.0 - feat_score)
        model_name = "note-cnn"
    else:
        fake_conf = 1.0 - feat_score
        model_name = "features-only"

    if fake_conf >= 0.6:
        verdict, confidence = "COUNTERFEIT", fake_conf
    elif fake_conf <= 0.4:
        verdict, confidence = "GENUINE", 1.0 - fake_conf
    else:
        verdict, confidence = "UNCERTAIN", 0.5

    return CurrencyResult(
        verdict=verdict,
        confidence=round(confidence, 2),
        denomination=denom,
        features=features,
        model=model_name,
    )

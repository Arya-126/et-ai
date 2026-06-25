"""Tests for the four newly-completed PS6 components: digital-arrest alerting,
multi-language localization, counterfeit-currency inference, and geospatial."""
import os

import pytest
from PIL import Image

from app.agents.alerting import store as alert_store
from app.agents.pipeline import process_report
from app.graph.factory import get_store
from app.schema import ReportInput


def test_alert_fires_on_high_risk_digital_arrest():
    alert_store.reset()
    r = process_report(ReportInput(
        raw_text="CBI: you are under digital arrest, stay on the video call and "
                 "transfer to refund.cbi@okaxis. Call +919876543210.",
    ))
    assert r.verdict == "HIGH RISK"
    assert r.alert is not None and r.alert.kind == "MHA"
    kinds = {a.kind for a in alert_store.all()}
    assert {"MHA", "TELECOM"} <= kinds            # both escalation + telecom flag


def test_localized_advice_is_non_english():
    en = process_report(ReportInput(raw_text="CBI digital arrest, pay refund.cbi@okaxis", language="en"))
    hi = process_report(ReportInput(raw_text="CBI digital arrest, pay refund.cbi@okaxis", language="hi"))
    assert hi.advice and hi.advice != en.advice   # Hindi advice differs from English


def test_geo_returns_points_and_hotspots():
    from data.seed import load_seed
    from app.routers.geo import geo

    load_seed(get_store())
    g = geo()
    assert len(g.hotspots) >= 3
    assert len(g.patrol_priority) >= 1
    assert all(p.lat and p.lng for p in g.hotspots)


def test_currency_infer_flags_fake_sample():
    from cv import infer
    from cv.generate_notes import ensure_samples

    folder = ensure_samples()
    fake = os.path.join(folder, "fake_2000.png")
    if not os.path.exists(fake):
        pytest.skip("samples not generated")
    res = infer.scan(Image.open(fake))
    assert res.verdict in ("GENUINE", "COUNTERFEIT", "UNCERTAIN")
    assert res.features                      # explainable breakdown present
    assert res.verdict != "GENUINE"          # a tampered note must not read genuine

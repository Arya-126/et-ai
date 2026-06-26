"""Call Guard + new fraud taxonomy + reputation/blocklist/analytics.
LLM-independent (rule-layer fallback path)."""
import json
import os

import pytest

from app.agents import reputation
from app.agents.intake import intake
from app.agents.registry import registry
from app.graph.factory import get_store
from app.rules import rules_only_classification
from app.schema import Report, ReportInput

DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reports.json")


def _seed():
    if not os.path.exists(DATA):
        pytest.skip("run `python -m data.generate` first")
    with open(DATA, encoding="utf-8") as f:
        raw = json.load(f)
    store = get_store()
    store.reset()
    for d in raw:
        store.write_report(Report(**d))
    return raw


@pytest.mark.parametrize("text,expected", [
    ("We have your son, he had an accident. Do not call police. Transfer money now.", "Kidnapping / Ransom"),
    ("Approve the request on your UPI app and read me the OTP to confirm the refund.", "OTP / UPI Fraud"),
    ("I morphed your photos and will leak them to your family unless you pay.", "Sextortion"),
])
def test_new_fraud_types_flagged(text, expected):
    c = rules_only_classification(intake(ReportInput(raw_text=text, caller_is_known=False)))
    assert c.verdict == "HIGH RISK"
    assert c.scam_type == expected


def test_unsaved_number_boosts_risk():
    text = "Sir, transfer the verification fee to clear your account."
    known = rules_only_classification(intake(ReportInput(raw_text=text, caller_is_known=True)))
    unknown = rules_only_classification(intake(ReportInput(raw_text=text, caller_is_known=False)))
    assert (unknown.confidence or 0) >= (known.confidence or 0)


def test_reputation_known_ring_number():
    _seed()
    bl = reputation.blocklist()
    assert bl, "blocklist should contain seeded ring numbers"
    top = bl[0]
    rep = reputation.lookup(top.phone)
    assert rep.known and rep.report_count >= 3


def test_unknown_number_reputation():
    _seed()
    rep = reputation.lookup("+910000000000")
    assert rep.known is False and rep.report_count == 0


def test_analytics_summary_non_empty():
    _seed()
    registry.reset()                      # force reload from the seed file
    from app.routers.analytics import analytics
    a = analytics()
    assert a["total_reports"] > 0
    assert a["scam_types"] and a["verdicts"]

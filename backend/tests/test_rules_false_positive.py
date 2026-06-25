"""The rubric explicitly penalizes false positives on the citizen tool. These
benign messages must NEVER read HIGH RISK. Run with the LLM offline so we test
the deterministic rule layer (the guarantee), not the model's mood.
"""
import pytest

from app.agents.intake import intake
from app.rules import rules_only_classification
from app.schema import ReportInput

BENIGN = [
    "Mom, dinner at 8? I'll bring dessert.",
    "Hi, your Amazon order has been shipped and is out for delivery today.",
    "Reminder: team standup at 10am, don't be late.",
    "Happy birthday bro! Let's catch up this weekend.",
    "Dear customer, your OTP is 482913. Do not share this OTP with anyone.",
    "The plumber is coming tomorrow between 2 and 4pm.",
    "Sis, can you pick up the kids from school today? Stuck in a meeting.",
    "Your table for 4 at 7:30pm is confirmed. See you tonight!",
]

SCAMS = [
    "This is CBI. You are under digital arrest. Stay on the video call and transfer "
    "money to refund.cbi@okaxis or face a non-bailable warrant.",
    "Customs seized a parcel with drugs in your name. Pay a verification fee to "
    "customs.clear@ybl immediately to avoid arrest.",
]


@pytest.mark.parametrize("text", BENIGN)
def test_benign_never_high_risk(text):
    report = intake(ReportInput(raw_text=text))
    c = rules_only_classification(report)
    assert c.verdict != "HIGH RISK", f"False positive on: {text!r} -> {c.verdict}"


@pytest.mark.parametrize("text", SCAMS)
def test_obvious_scams_flagged(text):
    report = intake(ReportInput(raw_text=text))
    c = rules_only_classification(report)
    assert c.verdict in ("HIGH RISK", "SUSPICIOUS"), f"Missed scam: {text!r}"

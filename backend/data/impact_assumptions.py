"""Disclosed assumptions behind the Impact / ROI dashboard.

Average loss figures are illustrative, anchored to publicly reported Indian
cyber-fraud ranges (I4C / NCRP / RBI press coverage, 2023-2025). They are
DEMONSTRATION estimates — shown transparently, not audited numbers.
"""
from __future__ import annotations

# Estimated average money at risk per HIGH-RISK case, by scam family (₹).
AVG_LOSS_BY_TYPE: dict[str, int] = {
    "Digital Arrest / Impersonation Scam": 1_100_000,
    "Kidnapping / Ransom": 300_000,
    "Sextortion": 80_000,
    "OTP / UPI Fraud": 45_000,
    "Loan-app / Recovery Scam": 25_000,
    "Investment / Task Scam": 250_000,
    "Parcel / Customs Scam": 90_000,
    "Lottery / Prize Scam": 35_000,
}
DEFAULT_AVG_LOSS = 60_000

# Detection-to-verdict latency we demonstrate (seconds).
AVG_RESPONSE_SECONDS = 2

# National-scale context for the projection (I4C: ~1930 complaints/day order of
# magnitude; used only to extrapolate "if deployed nationally").
NATIONAL_DAILY_COMPLAINTS = 6_000

SOURCES_NOTE = (
    "Illustrative estimates anchored to publicly reported I4C / NCRP cyber-fraud "
    "ranges (2023-2025). Demonstration figures on synthetic data — not audited."
)


def avg_loss(scam_type: str | None) -> int:
    return AVG_LOSS_BY_TYPE.get(scam_type or "", DEFAULT_AVG_LOSS)

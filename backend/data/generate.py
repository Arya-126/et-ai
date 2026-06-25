"""Synthetic data generator. THE most important pre-work: no planted rings =
nothing for Louvain to find = dead demo.

Produces ~200 reports:
  - 3 planted fraud RINGS: each ring = many victims sharing a UPI handle + mule
    account + device fingerprint + scam script, spread across 2-3 districts.
  - ~150 NOISE reports: isolated one-off scams (unique infra) and benign
    messages, so Louvain has to *separate* signal from noise.

Holds back 5 reports (incl. "Lakshmi") in holdback.json for live demo injection.

Run: python -m data.generate
"""
from __future__ import annotations

import json
import os
import random

from app.schema import Report
from data.scam_scripts import SCRIPTS, SCRIPTS_BY_ID

random.seed(42)
HERE = os.path.dirname(__file__)

FIRST = ["Lakshmi", "Ramesh", "Anita", "Suresh", "Priya", "Vijay", "Meena", "Arjun",
         "Kavya", "Mohan", "Geetha", "Rahul", "Divya", "Sanjay", "Latha", "Naveen",
         "Pooja", "Karthik", "Shobha", "Deepak", "Nisha", "Ganesh", "Reshma", "Vikram"]

# ring -> districts
RING_DISTRICTS = {
    "A": ["Bengaluru", "Mysuru", "Mandya"],
    "B": ["Delhi", "Gurugram", "Noida"],
    "C": ["Mumbai", "Pune", "Thane"],
}
NOISE_DISTRICTS = ["Chennai", "Hyderabad", "Kolkata", "Jaipur", "Ahmedabad",
                   "Lucknow", "Kochi", "Bhopal", "Patna", "Surat", "Bengaluru", "Delhi"]

BENIGN_MESSAGES = [
    "Mom, dinner at 8? I'll bring dessert.",
    "Hi, your Amazon order has been shipped and is out for delivery today.",
    "Reminder: team standup at 10am, don't be late.",
    "Happy birthday bro! Let's catch up this weekend.",
    "Dear customer, your OTP is 482913. Do not share this OTP with anyone.",
    "The plumber is coming tomorrow between 2 and 4pm.",
    "Your electricity bill of Rs 1,240 is due on the 28th. Pay via the official app.",
    "Sis, can you pick up the kids from school today? Stuck in a meeting.",
    "Your table for 4 at 7:30pm is confirmed. See you tonight!",
    "Project deadline moved to Friday. Please update the tracker.",
]

ONE_OFF_SCAMS = [
    "You have won Rs 25 lakh in the KBC lottery! Send Rs 5000 processing fee to claim.",
    "Your electricity will be disconnected tonight. Call this officer immediately.",
    "Congratulations, your number won a lucky draw. Share your bank details to receive prize.",
    "Job offer: work from home, earn Rs 5000/day. Pay Rs 999 registration to start.",
    "Your SBI account is blocked. Update PAN by clicking this link now.",
]


def _phone() -> str:
    return "+91" + str(random.randint(6, 9)) + "".join(str(random.randint(0, 9)) for _ in range(9))


def _fill(template: str, upi: str, phone: str, account: str) -> str:
    return (template.replace("{upi}", upi)
                    .replace("{phone}", phone)
                    .replace("{account}", account))


def _ring_reports(ring_key: str, script_id: str, n: int) -> list[Report]:
    """A planted ring: n victims sharing one UPI + account + device + script."""
    script = SCRIPTS_BY_ID[script_id]
    upi = f"{script.family.lower().replace(' ', '')}.{ring_key.lower()}@okaxis"
    account = "".join(str(random.randint(0, 9)) for _ in range(14))
    device = f"DEV-{ring_key}-{random.randint(1000, 9999)}"
    controller_phone = _phone()  # one shared controller number ties the ring
    districts = RING_DISTRICTS[ring_key]

    reports = []
    for i in range(n):
        text = _fill(script.template, upi, controller_phone, account)
        reports.append(Report(
            raw_text=text,
            channel=random.choice(["call", "whatsapp", "sms"]),
            claimed_authority=script.authority,
            phone=controller_phone,
            upi_id=upi,
            account_no=account,
            device_hint=device,
            reporter_id=f"{random.choice(FIRST)}-{ring_key}{i:02d}",
            district=random.choice(districts),
            matched_script_id=script.id,
            verdict="HIGH RISK",
            scam_type=f"{script.family} Scam",
            confidence=round(random.uniform(0.88, 0.98), 2),
            red_flags=script.red_flags[:3],
            advice="Do not transfer money or share OTP. Report to 1930.",
        ))
    return reports


def _noise_reports(n_scam: int, n_benign: int) -> list[Report]:
    out = []
    for i in range(n_scam):
        text = random.choice(ONE_OFF_SCAMS)
        # each one-off has UNIQUE infra -> stays an isolated small component
        out.append(Report(
            raw_text=text,
            channel=random.choice(["sms", "whatsapp", "call"]),
            phone=_phone(),
            upi_id=f"oneoff{i}@{random.choice(['ybl', 'paytm', 'oksbi'])}",
            reporter_id=f"{random.choice(FIRST)}-noise{i:03d}",
            district=random.choice(NOISE_DISTRICTS),
            verdict="SUSPICIOUS",
            scam_type="One-off scam",
            confidence=round(random.uniform(0.5, 0.7), 2),
            red_flags=["Unsolicited prize / fee request"],
            advice="Be cautious. Do not pay any fee. Verify independently.",
        ))
    for i in range(n_benign):
        out.append(Report(
            raw_text=random.choice(BENIGN_MESSAGES),
            channel=random.choice(["whatsapp", "sms"]),
            reporter_id=f"{random.choice(FIRST)}-ok{i:03d}",
            district=random.choice(NOISE_DISTRICTS),
            verdict="LIKELY SAFE",
            scam_type="No clear scam pattern",
            confidence=round(random.uniform(0.05, 0.2), 2),
            red_flags=[],
            advice="Nothing matches known scam patterns.",
        ))
    return out


def _holdback() -> list[Report]:
    """5 reports injected live. 'Lakshmi' shares Ring A's UPI+account so the
    ring visibly grows on stage; 4 others seed/extend rings B and C."""
    a = SCRIPTS_BY_ID["digital_arrest_cbi"]
    lakshmi = Report(
        raw_text=_fill(a.template, "digitalarrest.a@okaxis", "+919876543210",
                       "ring-A shared account"),
        channel="call",
        claimed_authority="CBI",
        phone="+919876543210",
        upi_id="digitalarrest.a@okaxis",      # MUST equal Ring A's UPI (see _ring_reports)
        account_no=None,
        device_hint="DEV-A-shared",
        reporter_id="Lakshmi-LIVE",
        district="Bengaluru",
        matched_script_id="digital_arrest_cbi",
    )
    return [lakshmi] + _ring_reports("A", "digital_arrest_cbi", 2)[:2] + \
        _ring_reports("B", "customs_parcel", 2)[:2]


def main() -> None:
    reports: list[Report] = []
    reports += _ring_reports("A", "digital_arrest_cbi", 22)
    reports += _ring_reports("B", "customs_parcel", 16)
    reports += _ring_reports("C", "ed_money_laundering", 13)
    reports += _noise_reports(n_scam=55, n_benign=95)
    random.shuffle(reports)

    with open(os.path.join(HERE, "reports.json"), "w", encoding="utf-8") as f:
        json.dump([r.model_dump(mode="json") for r in reports], f, indent=2, default=str)
    with open(os.path.join(HERE, "holdback.json"), "w", encoding="utf-8") as f:
        json.dump([r.model_dump(mode="json") for r in _holdback()], f, indent=2, default=str)

    print(f"Wrote {len(reports)} seed reports + 5 holdback reports.")
    print("Rings planted: A=digital_arrest_cbi(22), B=customs_parcel(16), C=ed_money_laundering(13)")


if __name__ == "__main__":
    main()

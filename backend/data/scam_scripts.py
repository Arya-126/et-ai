"""Library of real-world Indian fraud scripts. Triple duty:
  1. Few-shot examples for the ClassifierAgent prompt.
  2. `ScamScript` nodes in the graph (reports MATCHES_SCRIPT a template).
  3. Templates the synthetic data generator fills to create planted rings.

Each script: id, family, authority, a fill-in template, and the canonical
red flags. Keep these legible — they double as demo talking points.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScamScript:
    id: str
    family: str           # short label, e.g. "digital_arrest_cbi"
    authority: str        # impersonated authority
    template: str         # {phone},{upi},{authority} placeholders
    red_flags: list[str] = field(default_factory=list)


SCRIPTS: list[ScamScript] = [
    ScamScript(
        id="digital_arrest_cbi",
        family="Digital Arrest",
        authority="CBI",
        template=(
            "This is Inspector Sharma from CBI. Your Aadhaar is linked to a money "
            "laundering case. A non-bailable warrant is issued. You are under digital "
            "arrest — stay on this video call and do not disconnect or inform anyone. "
            "To clear your name, transfer a refundable security deposit to {upi}. "
            "Call me back on {phone}."
        ),
        red_flags=[
            "Impersonates CBI", "Claims 'digital arrest'",
            "Threatens non-bailable warrant", "Demands secrecy from family",
            "Asks to transfer a 'security deposit'",
        ],
    ),
    ScamScript(
        id="customs_parcel",
        family="Parcel Scam",
        authority="Customs",
        template=(
            "Customs Department here. A parcel in your name containing illegal drugs "
            "and fake passports has been seized at the airport. Your number is involved "
            "in narcotics trafficking. Pay a verification fee to {upi} immediately to "
            "avoid arrest, and stay on the line with officer at {phone}."
        ),
        red_flags=[
            "Impersonates Customs", "Fake seized-parcel pretext",
            "Accuses you of narcotics", "Demands a verification fee",
        ],
    ),
    ScamScript(
        id="trai_disconnect",
        family="Digital Arrest",
        authority="TRAI",
        template=(
            "TRAI notice: your mobile number will be disconnected in 2 hours due to "
            "illegal activity complaints. Press 9 to talk to an officer. Your Aadhaar "
            "is linked to a criminal case in Mumbai cyber cell. Transfer funds to {upi} "
            "for verification or face arrest. Officer number {phone}."
        ),
        red_flags=[
            "Impersonates TRAI", "Threatens SIM disconnection",
            "Links Aadhaar to a crime", "Asks to transfer funds for 'verification'",
        ],
    ),
    ScamScript(
        id="ed_money_laundering",
        family="Digital Arrest",
        authority="ED",
        template=(
            "Enforcement Directorate. Your bank account is flagged in a Rs 20 crore "
            "money laundering investigation. You must remain on this video call under "
            "digital arrest. Do not tell your family. Move your balance to a 'safe' "
            "RBI account {account} to prove your funds are clean. Reach us at {phone}."
        ),
        red_flags=[
            "Impersonates ED", "Claims 'digital arrest'",
            "Asks to move money to a 'safe' account", "Demands secrecy",
        ],
    ),
    ScamScript(
        id="bank_kyc_otp",
        family="KYC / OTP",
        authority="bank",
        template=(
            "Dear customer, your bank account will be blocked today as KYC is pending. "
            "Click the link and share the OTP sent to your phone to complete KYC, or "
            "your account is frozen. For help call {phone}."
        ),
        red_flags=[
            "Fake KYC-expiry urgency", "Asks you to share OTP",
            "Threatens to freeze the account",
        ],
    ),
    ScamScript(
        id="police_cyber_cell",
        family="Digital Arrest",
        authority="Police",
        template=(
            "Mumbai Cyber Cell. We have a complaint that your photos were used in a "
            "child abuse case. To avoid public arrest, stay on this video call and pay "
            "a settlement to {upi}. Keep this strictly confidential. Officer {phone}."
        ),
        red_flags=[
            "Impersonates police / cyber cell", "Shocking false accusation",
            "Demands a secret 'settlement'", "Pressure to stay on video call",
        ],
    ),
    # ---- call-fraud families (Call Guard) -------------------------------
    ScamScript(
        id="otp_upi_collect",
        family="OTP / UPI Fraud",
        authority="bank",
        template=(
            "Sir, I am calling from your bank. To reverse the wrong debit I have sent a "
            "request on your UPI app — just approve it and read me the 6-digit OTP to "
            "confirm the refund of {amount}. Do it now or the amount is lost. Account {account}."
        ),
        red_flags=[
            "Asks you to share an OTP", "Asks you to APPROVE a UPI collect request",
            "Fake 'refund' / wrong-debit pretext", "Creates false urgency",
        ],
    ),
    ScamScript(
        id="ransom_family_emergency",
        family="Kidnapping / Ransom",
        authority="kidnapper",
        template=(
            "Listen carefully. We have your son. He had an accident and is with us. "
            "If you call the police he is finished. Transfer {amount} to {upi} right now "
            "and do not disconnect this call or tell anyone. We are watching you."
        ),
        red_flags=[
            "Claims a relative is kidnapped / in an accident", "Forbids calling police",
            "Demands immediate ransom transfer", "Extreme fear + secrecy pressure",
            "Often uses an AI-cloned voice",
        ],
    ),
    ScamScript(
        id="sextortion",
        family="Sextortion",
        authority="blackmailer",
        template=(
            "I have recorded our video call and morphed your photos. I will send them to "
            "your family and post them online unless you pay {amount} to {upi} in the next "
            "hour. I have your contact list. Don't test me."
        ),
        red_flags=[
            "Threatens to leak intimate / morphed images", "Blackmail after a video call",
            "Threatens to contact your family", "Demands money to stay silent",
        ],
    ),
    ScamScript(
        id="loan_recovery",
        family="Loan-app / Recovery",
        authority="recovery agent",
        template=(
            "This is recovery for the loan app. Your EMI is overdue. Pay {amount} to {upi} "
            "today or we send your morphed photo to everyone in your contacts and mark you "
            "a defaulter at your office. Final warning."
        ),
        red_flags=[
            "Predatory loan-app recovery threat", "Threatens to shame you to contacts",
            "Demands immediate payment to a UPI handle",
        ],
    ),
    ScamScript(
        id="investment_task",
        family="Investment / Task Scam",
        authority="investment advisor",
        template=(
            "Congratulations! Complete simple tasks and earn daily. Your wallet shows a "
            "profit of {amount} — to withdraw, first deposit a {amount} activation fee to "
            "{upi}. Guaranteed 30% returns, our VIP group never loses."
        ),
        red_flags=[
            "Promises guaranteed / unrealistic returns", "Pay-to-withdraw 'fee' trap",
            "Task / part-time job earning bait", "Pressure from a VIP group",
        ],
    ),
]

SCRIPTS_BY_ID = {s.id: s for s in SCRIPTS}
DIGITAL_ARREST_SCRIPTS = [s for s in SCRIPTS if s.family == "Digital Arrest"]


def few_shot_block(max_examples: int = 2) -> str:
    """Render a compact few-shot block for the classifier system prompt."""
    lines = []
    for s in SCRIPTS[:max_examples]:
        lines.append(
            f"- [{s.authority}] {s.template[:160]}...  -> HIGH RISK, "
            f"scam_type='{s.family} Scam', flags={s.red_flags[:3]}"
        )
    return "\n".join(lines)

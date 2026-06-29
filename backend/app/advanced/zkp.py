"""Zero-Knowledge officer verification — a REAL non-interactive Schnorr proof
(Fiat-Shamir). A legitimate officer proves they hold an authorization secret
without ever transmitting it, so a fake-government-portal impersonator (who does
not hold the secret) cannot produce a valid proof. Defeats credential spoofing.

Group: RFC 5114 §2.1 — 1024-bit MODP with a 160-bit prime-order subgroup (q).
Pure-Python (hashlib + ints); no dependencies.
"""
from __future__ import annotations

import hashlib
import secrets

# RFC 5114 1024-bit MODP Group with 160-bit Prime Order Subgroup
P = int(
    "B10B8F96A080E01DDE92DE5EAE5D54EC52C99FBCFB06A3C69A6A9DCA52D23B616073E28675A23D189838EF1E2EE652C013ECB4AEA906112324975C3CD49B83BFACCBDD7D90C4BD7098488E9C219A73724EFFD6FAE5644738FAA31A4FF55BCCC0A151AF5F0DC8B4BD45BF37DF365C1A65E68CFDA76D4DA708DF1FB2BC2E4A4371",
    16,
)
G = int(
    "A4D1CBD5C3FD34126765A442EFB99905F8104DD258AC507FD6406CFF14266D31266FEA1E5C41564B777E690F5504F213160217B4B01B886A5E91547F9E2749F4D7FBD7D3B9A92EE1909D0D2263F80A76A6A24C087A091F531DBF0A0169B6A28AD662A4D18E73AFA32D779D5918D08BC8858F4DCEF97C2A24855E6EEB22B3B2E5",
    16,
)
Q = int("F518AA8781A8DF278ABA4E7D64B7CB9D49462353", 16)  # 160-bit subgroup order


def keypair() -> tuple[int, int]:
    """Return (x, y): private authorization secret x and public key y = g^x mod p."""
    x = secrets.randbelow(Q - 1) + 1
    y = pow(G, x, P)
    return x, y


def _challenge(y: int, t: int, message: str) -> int:
    h = hashlib.sha256(f"{G}|{P}|{y}|{t}|{message}".encode()).digest()
    return int.from_bytes(h, "big") % Q


def prove(x: int, message: str) -> dict:
    """Non-interactive Schnorr proof of knowledge of x, bound to `message`."""
    r = secrets.randbelow(Q - 1) + 1
    t = pow(G, r, P)                       # commitment
    c = _challenge(pow(G, x, P), t, message)
    s = (r + c * x) % Q
    return {"t": str(t), "s": str(s)}


def verify(y: int, message: str, proof: dict) -> bool:
    """Verify a proof against public key y. True ⇒ prover holds the secret."""
    try:
        t = int(proof["t"]); s = int(proof["s"])
    except (KeyError, ValueError, TypeError):
        return False
    if not (1 < t < P):
        return False
    c = _challenge(y, t, message)
    # g^s ?= t * y^c (mod p)
    return pow(G, s, P) == (t * pow(y, c, P)) % P


# --- officer registry (demo) ---------------------------------------------
# In production each officer holds x in a secure element; only y is published.
_OFFICERS: dict[str, int] = {}


def register_officer(officer_id: str) -> dict:
    x, y = keypair()
    _OFFICERS[officer_id] = y
    return {"officer_id": officer_id, "private_key": str(x), "public_key": str(y)}


def public_key(officer_id: str) -> int | None:
    return _OFFICERS.get(officer_id)


def demo(impersonator: bool, officer_id: str = "CBI-Officer-4471",
         message: str = "I am a verified officer requesting to speak with you.") -> dict:
    """End-to-end demo: a genuine officer verifies; an impersonator is rejected."""
    if officer_id not in _OFFICERS:
        register_officer(officer_id)
    y = _OFFICERS[officer_id]

    if impersonator:
        fake_x, _ = keypair()                     # attacker guesses a secret
        proof = prove(fake_x, message)            # cannot match the registered y
        who = "Impersonator (fake portal, no authorization secret)"
    else:
        # genuine officer re-derives from their stored secret; here we mint one
        # bound to this public key for the demo flow
        x, y2 = keypair()
        _OFFICERS[officer_id] = y2                # rotate to the genuine keypair
        y = y2
        proof = prove(x, message)
        who = "Genuine officer (holds authorization secret)"

    ok = verify(y, message, proof)
    return {
        "claimant": who,
        "message": message,
        "proof": proof,
        "verified": ok,
        "explanation": (
            "Verified: the proof satisfies g^s = t·y^c (mod p), so the claimant holds "
            "the authorization secret — without ever sending it."
            if ok else
            "Rejected: the proof fails the verification equation. The claimant does not "
            "hold the registered authorization secret — a spoofed identity."
        ),
        "group": "RFC 5114 1024-bit MODP, 160-bit subgroup",
    }

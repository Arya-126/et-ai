"""SIP / network telephony forensics. Parses a SIP INVITE and scores network-layer
anomalies that betray a call originating from an illicit VoIP fraud compound rather
than a legitimate carrier or government gateway:

  - source IP is a bogon / private / known-bad range behind an "authority" claim
  - Via/Contact host disagrees with the claimed origin (route manipulation)
  - bulk-dialler / scanner User-Agents (friendly-scanner, sipcli, sipvicious)
  - international transit for a domestic-authority caller (+91 CBI from abroad)
  - IP-fragmentation / odd transport flags used to evade carrier DPI firewalls
  - many anonymising Via hops

These are real SIP-security heuristics. Live packet capture (DPI) is simulated:
the input is the SIP header text + a small packet-meta dict that a DPI tap would
provide. Returns a network-risk score that Call Guard folds into its verdict.
"""
from __future__ import annotations

import ipaddress
import re

BAD_USER_AGENTS = re.compile(
    r"friendly-scanner|sipvicious|sipcli|sip-?scan|warvox|VaxSIPUserAgent|sundayddr", re.I
)
AUTHORITY_HINT = re.compile(r"cbi|police|trai|customs|income\s*tax|cyber|gov", re.I)


def _header(text: str, name: str) -> str | None:
    m = re.search(rf"^{name}\s*:\s*(.+)$", text, re.I | re.M)
    return m.group(1).strip() if m else None


def _first_ip(s: str | None) -> str | None:
    if not s:
        return None
    m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", s)
    return m.group(1) if m else None


def _ip_class(ip: str | None) -> str:
    if not ip:
        return "unknown"
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return "invalid"
    if a.is_private:
        return "private"
    if a.is_loopback or a.is_reserved or a.is_unspecified:
        return "bogon"
    return "public"


def analyze(sip_text: str, packet_meta: dict | None = None) -> dict:
    """Score SIP + DPI metadata. packet_meta may include {src_ip, src_country,
    transport, fragmented, ttl}."""
    meta = packet_meta or {}
    findings: list[str] = []
    score = 0.0

    via = _header(sip_text, "Via")
    frm = _header(sip_text, "From")
    contact = _header(sip_text, "Contact")
    ua = _header(sip_text, "User-Agent") or ""

    via_ip = _first_ip(via)
    contact_ip = _first_ip(contact)
    src_ip = meta.get("src_ip") or via_ip

    claims_authority = bool(AUTHORITY_HINT.search(frm or "")) or bool(AUTHORITY_HINT.search(contact or ""))

    # 1. bulk-dialler / scanner signatures
    if BAD_USER_AGENTS.search(ua):
        score += 0.4
        findings.append(f"Bulk-dialler / scanner User-Agent: '{ua}'")

    # 2. source IP class
    cls = _ip_class(src_ip)
    if cls in ("bogon", "invalid"):
        score += 0.3
        findings.append(f"Source IP {src_ip} is a bogon/invalid address (origin masking)")
    elif cls == "private" and claims_authority:
        score += 0.2
        findings.append(f"'Authority' call routed from a private IP {src_ip} (not a carrier gateway)")

    # 3. Via vs Contact host mismatch → route manipulation
    if via_ip and contact_ip and via_ip != contact_ip:
        score += 0.2
        findings.append(f"Via host {via_ip} ≠ Contact host {contact_ip} (route manipulation)")

    # 4. international transit for a domestic authority
    country = (meta.get("src_country") or "").upper()
    if claims_authority and country and country not in ("IN", "INDIA"):
        score += 0.35
        findings.append(f"Domestic-authority caller transiting from {country} (offshore fraud compound)")

    # 5. fragmentation / DPI-evasion transport flags
    if meta.get("fragmented"):
        score += 0.25
        findings.append("IP fragmentation flagged — common carrier-firewall/DPI evasion")
    ttl = meta.get("ttl")
    if isinstance(ttl, int) and ttl < 32:
        score += 0.1
        findings.append(f"Unusually low TTL ({ttl}) — long anonymising relay path")

    # 6. many Via hops (anonymising proxies)
    hops = len(re.findall(r"^Via\s*:", sip_text, re.I | re.M))
    if hops >= 3:
        score += 0.15
        findings.append(f"{hops} Via hops — chained anonymising proxies")

    score = min(score, 1.0)
    verdict = "ILLICIT GATEWAY" if score >= 0.6 else "SUSPICIOUS" if score >= 0.3 else "CLEAN"
    return {
        "network_risk": round(score, 2),
        "verdict": verdict,
        "findings": findings or ["No network-layer anomalies detected."],
        "parsed": {"via_ip": via_ip, "contact_ip": contact_ip, "src_ip": src_ip,
                   "src_class": cls, "user_agent": ua, "via_hops": hops,
                   "claims_authority": claims_authority},
    }


# --- disclosed synthetic sample packets for the demo ----------------------
SAMPLES: dict[str, dict] = {
    "fraud_compound": {
        "label": "Digital-arrest call from an offshore VoIP compound",
        "sip": (
            "INVITE sip:+919876543210@gateway.in SIP/2.0\r\n"
            "Via: SIP/2.0/UDP 45.131.x.10:5060;branch=z9hG4bK1\r\n"
            "Via: SIP/2.0/UDP 10.8.0.4:5060;branch=z9hG4bK2\r\n"
            "Via: SIP/2.0/UDP 192.168.10.7:5060;branch=z9hG4bK3\r\n"
            "From: \"CBI Cyber Cell\" <sip:cbi@45.131.x.10>\r\n"
            "Contact: <sip:cbi@103.27.x.55>\r\n"
            "User-Agent: friendly-scanner\r\n"
        ),
        "meta": {"src_ip": "45.131.10.10", "src_country": "KH", "transport": "UDP",
                 "fragmented": True, "ttl": 24},
    },
    "legit_carrier": {
        "label": "Legitimate call via an Indian carrier gateway",
        "sip": (
            "INVITE sip:+919876543210@ims.jio.com SIP/2.0\r\n"
            "Via: SIP/2.0/TLS 49.45.2.20:5061;branch=z9hG4bKabc\r\n"
            "From: \"Customer Care\" <sip:care@ims.jio.com>\r\n"
            "Contact: <sip:care@49.45.2.20>\r\n"
            "User-Agent: JioCore/5.2\r\n"
        ),
        "meta": {"src_ip": "49.45.2.20", "src_country": "IN", "transport": "TLS",
                 "fragmented": False, "ttl": 118},
    },
}

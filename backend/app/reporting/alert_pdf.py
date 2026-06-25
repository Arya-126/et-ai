"""Alert artifact PDF (Component 1) — the MHA/I4C escalation document generated
for a HIGH RISK digital-arrest session. Pure ReportLab, same look as the
intelligence package.
"""
from __future__ import annotations

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schema import Alert

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "out")
NAVY = colors.HexColor("#0b2545")
RED = colors.HexColor("#c1121f")
GREY = colors.HexColor("#5c677d")


def build_alert_pdf(alert: Alert) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"alert_{alert.alert_id}.pdf")
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H1", parent=ss["Title"], textColor=NAVY, fontSize=20, spaceAfter=4))
    ss.add(ParagraphStyle("Sub", parent=ss["Normal"], textColor=GREY, fontSize=10, spaceAfter=12))
    ss.add(ParagraphStyle("Red", parent=ss["Normal"], textColor=RED, fontSize=12, leading=16))

    doc = SimpleDocTemplate(path, pagesize=A4, title=f"Alert {alert.alert_id}")
    flow = [
        Paragraph(f"{alert.kind} Cybercrime Alert", ss["H1"]),
        Paragraph(
            f"Alert {alert.alert_id} · generated {alert.created:%Y-%m-%d %H:%M} · "
            f"AUTOMATED — PRE-TRANSFER INTERVENTION", ss["Sub"]),
        Paragraph(f"&#9888; {alert.summary}", ss["Red"]),
        Spacer(1, 8),
    ]

    rows = [
        ["Routed to", alert.target],
        ["Scam type", alert.scam_type or "—"],
        ["Controller number", alert.phone or "—"],
        ["Payment handle (UPI)", alert.upi_id or "—"],
        ["District", alert.district or "—"],
        ["Source report", alert.report_id],
    ]
    t = Table(rows, colWidths=[55 * mm, 115 * mm])
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 14))
    flow.append(Paragraph(
        "<i>Demonstration artifact generated from a synthetic dataset for the ET AI "
        "Hackathon 2026. No real MHA/I4C or telecom systems were contacted.</i>", ss["Sub"]))
    doc.build(flow)
    return path

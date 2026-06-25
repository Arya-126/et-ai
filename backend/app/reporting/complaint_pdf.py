"""NCRB / cybercrime.gov.in complaint draft (Component 5) — compiles a citizen's
report into a pre-filled complaint the user can submit to 1930 / the National
Cyber Crime Reporting Portal.
"""
from __future__ import annotations

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schema import Report

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "out")
NAVY = colors.HexColor("#0b2545")
GREY = colors.HexColor("#5c677d")


def build_complaint_pdf(report: Report) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"complaint_{report.report_id}.pdf")
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H1", parent=ss["Title"], textColor=NAVY, fontSize=19, spaceAfter=4))
    ss.add(ParagraphStyle("Sub", parent=ss["Normal"], textColor=GREY, fontSize=10, spaceAfter=12))
    ss.add(ParagraphStyle("H2", parent=ss["Heading2"], textColor=NAVY, fontSize=12, spaceBefore=8))

    doc = SimpleDocTemplate(path, pagesize=A4, title=f"Cybercrime complaint {report.report_id}")
    flow = [
        Paragraph("National Cyber Crime Reporting — Complaint Draft", ss["H1"]),
        Paragraph(
            f"Prepared {datetime.now():%Y-%m-%d %H:%M} · Helpline 1930 · cybercrime.gov.in", ss["Sub"]),
        Paragraph("1. Category", ss["H2"]),
        Paragraph(f"Online Financial Fraud — {report.scam_type or 'Suspected scam'} "
                  f"(risk assessment: {report.verdict or 'N/A'}, "
                  f"confidence {int((report.confidence or 0)*100)}%).", ss["Normal"]),
        Paragraph("2. Suspect details (as reported)", ss["H2"]),
    ]
    rows = [
        ["Claimed authority", report.claimed_authority or "—"],
        ["Caller number", report.phone or "—"],
        ["UPI handle", report.upi_id or "—"],
        ["Account number", report.account_no or "—"],
        ["Channel", report.channel],
        ["District", report.district or "—"],
    ]
    t = Table(rows, colWidths=[50 * mm, 120 * mm])
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    flow.append(t)
    flow.append(Paragraph("3. Incident description", ss["H2"]))
    flow.append(Paragraph((report.raw_text or "").replace("\n", "<br/>"), ss["Normal"]))
    if report.red_flags:
        flow.append(Paragraph("4. Red flags identified", ss["H2"]))
        for f in report.red_flags:
            flow.append(Paragraph(f"• {f}", ss["Normal"]))
    flow.append(Spacer(1, 12))
    flow.append(Paragraph(
        "<i>Auto-drafted by Citizen Fraud Shield. Review, add your personal details, and "
        "submit at cybercrime.gov.in or call 1930. Demonstration uses synthetic data.</i>",
        ss["Sub"]))
    doc.build(flow)
    return path

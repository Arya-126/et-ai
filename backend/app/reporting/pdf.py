"""ReportLab intelligence package — the court-ready PDF the LE dashboard
generates for one ring. Pure-Python (no GTK), so it just works on Windows.

Sections: cover, ring summary, prioritized infrastructure (PageRank), linked
reports table, and a synthetic-data disclaimer.
"""
from __future__ import annotations

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from app.schema import GraphDTO, Ring, ScoredNode

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "out")

NAVY = colors.HexColor("#0b2545")
RED = colors.HexColor("#c1121f")
GREY = colors.HexColor("#5c677d")


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H1", parent=ss["Title"], textColor=NAVY, fontSize=22, spaceAfter=4))
    ss.add(ParagraphStyle("Sub", parent=ss["Normal"], textColor=GREY, fontSize=10, spaceAfter=12))
    ss.add(ParagraphStyle("H2", parent=ss["Heading2"], textColor=NAVY, fontSize=13, spaceBefore=10))
    ss.add(ParagraphStyle("Kingpin", parent=ss["Normal"], textColor=RED, fontSize=12, leading=16))
    return ss


def build_package_pdf(ring: Ring, subgraph: GraphDTO, centrality: list[ScoredNode]) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"intelligence_package_{ring.ring_id}.pdf")
    ss = _styles()
    doc = SimpleDocTemplate(path, pagesize=A4, title=f"Intelligence Package {ring.ring_id}")
    flow = []

    # Cover
    flow.append(Paragraph("Fraud Network Intelligence Package", ss["H1"]))
    flow.append(Paragraph(
        f"Ring {ring.ring_id} &nbsp;·&nbsp; generated {datetime.now():%Y-%m-%d %H:%M} "
        f"&nbsp;·&nbsp; CONFIDENTIAL — LAW ENFORCEMENT USE", ss["Sub"]))

    # Summary
    flow.append(Paragraph("1. Ring summary", ss["H2"]))
    summary = [
        ["Linked reports (victims)", str(ring.report_count)],
        ["Total nodes in ring", str(ring.size)],
        ["Districts affected", ", ".join(ring.districts) or "—"],
        ["Detection method", "Louvain community detection + PageRank centrality (GDS)"],
    ]
    t = Table(summary, colWidths=[60 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    flow.append(t)

    # Kingpin
    flow.append(Paragraph("2. Priority target (PageRank)", ss["H2"]))
    if ring.top_node:
        k = ring.top_node
        flow.append(Paragraph(
            f"&#9733; ARREST PRIORITY #1: <b>{k.value}</b> ({k.label}) — "
            f"PageRank {k.score}. This node sits at the center of the ring and "
            f"ties the largest number of victim reports together.", ss["Kingpin"]))
    else:
        flow.append(Paragraph("No dominant central node identified.", ss["Normal"]))

    # Centrality table
    flow.append(Spacer(1, 6))
    rows = [["#", "Entity", "Type", "PageRank"]]
    for i, n in enumerate(centrality[:10], 1):
        rows.append([str(i), n.value, n.label, f"{n.score}"])
    ct = Table(rows, colWidths=[10 * mm, 80 * mm, 40 * mm, 40 * mm])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2f7")]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    flow.append(ct)

    # Linked reports
    flow.append(Paragraph("3. Linked reports & infrastructure", ss["H2"]))
    report_nodes = [n for n in subgraph.nodes if n.label == "Report"]
    infra = [n for n in subgraph.nodes if n.label in ("UPI", "Account", "PhoneNumber", "Device")]
    flow.append(Paragraph(
        f"{len(report_nodes)} victim reports are connected through "
        f"{len(infra)} shared infrastructure nodes (UPI handles, mule accounts, "
        f"phone numbers, device fingerprints). The shared infrastructure is the "
        f"evidentiary spine linking otherwise-separate complaints into one operation.",
        ss["Normal"]))
    flow.append(Spacer(1, 6))
    irows = [["Entity", "Type"]]
    for n in infra[:20]:
        irows.append([n.value, n.label])
    it = Table(irows, colWidths=[120 * mm, 50 * mm])
    it.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    flow.append(it)

    # Disclaimer
    flow.append(Spacer(1, 14))
    flow.append(Paragraph(
        "<i>Demonstration notice: this package was generated from a synthetic dataset "
        "built for the ET AI Hackathon 2026. Ring structure was planted to validate the "
        "detection pipeline. No real personal data is depicted.</i>", ss["Sub"]))

    doc.build(flow)
    return path

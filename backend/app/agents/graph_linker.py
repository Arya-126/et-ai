"""GraphLinkerAgent — writes the classified report's entities and edges into the
graph. Shared UPI handles / accounts / devices are what make rings *form*, so a
report is only linked once it has a verdict (we still graph SUSPICIOUS/HIGH RISK;
LIKELY SAFE reports are recorded but contribute little structure).
"""
from __future__ import annotations

from app.graph.factory import get_store
from app.schema import Report


def link(report: Report) -> Report:
    get_store().write_report(report)
    return report

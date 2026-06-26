"""In-process registry of processed reports, for analytics. Lazy-loads the seed
(`data/reports.json`) so trends cover the synthetic baseline, and the pipeline
appends each live report. Separate from the graph (which doesn't expose per-report
attributes in its DTO)."""
from __future__ import annotations

import json
import os

from app.schema import Report

_SEED = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                     "data", "reports.json")


class ReportRegistry:
    def __init__(self) -> None:
        self._reports: list[Report] = []
        self._loaded = False

    def _ensure(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if os.path.exists(_SEED):
            try:
                with open(_SEED, encoding="utf-8") as f:
                    self._reports = [Report(**d) for d in json.load(f)]
            except Exception:  # noqa: BLE001 — analytics is best-effort
                self._reports = []

    def add(self, report: Report) -> None:
        self._ensure()
        self._reports.append(report)

    def all(self) -> list[Report]:
        self._ensure()
        return list(self._reports)

    def reset(self) -> None:
        self._reports.clear()
        self._loaded = False


registry = ReportRegistry()

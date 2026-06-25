"""End-to-end spine: a raw scam string flows intake -> classifier -> graph_linker
and lands nodes/edges; a planted seed produces detectable rings with a kingpin;
the intelligence package PDF renders. LLM-independent (rule fallback path)."""
import json
import os

from app.agents import classifier, graph_linker, intake
from app.agents import package as package_agent
from app.graph.factory import get_store
from app.schema import Report, ReportInput

DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reports.json")


def test_single_report_lands_in_graph():
    report = intake.intake(ReportInput(
        raw_text="CBI digital arrest. Transfer to refund.cbi@okaxis now.",
    ))
    report = classifier.apply_to(report)      # rules fallback if Ollama down
    assert report.verdict in ("HIGH RISK", "SUSPICIOUS", "LIKELY SAFE")
    assert report.upi_id == "refund.cbi@okaxis"

    graph_linker.link(report)
    g = get_store().get_graph()
    values = {n.value for n in g.nodes}
    assert "refund.cbi@okaxis" in values


def _seed_from_disk():
    with open(DATA, encoding="utf-8") as f:
        raw = json.load(f)
    store = get_store()
    store.reset()
    for d in raw:
        store.write_report(Report(**d))
    return store


def test_rings_detected_with_kingpin():
    if not os.path.exists(DATA):
        import pytest
        pytest.skip("run `python -m data.generate` first")
    store = _seed_from_disk()
    rings = store.detect_rings()
    assert len(rings) >= 3, f"expected >=3 planted rings, got {len(rings)}"
    biggest = rings[0]
    assert biggest.report_count >= 10
    assert biggest.top_node is not None
    assert len(biggest.districts) >= 1


def test_intelligence_package_pdf():
    if not os.path.exists(DATA):
        import pytest
        pytest.skip("run `python -m data.generate` first")
    store = _seed_from_disk()
    ring_id = store.detect_rings()[0].ring_id
    pkg = package_agent.build(ring_id)
    assert pkg is not None
    assert os.path.exists(pkg.pdf_path)
    assert pkg.ring.top_node is not None

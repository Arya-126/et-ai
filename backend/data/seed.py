"""Load the synthetic seed into the graph store (fast path — writes pre-classified
reports directly, bypassing the LLM). Holds back the 5 demo reports.

Run: python -m data.seed   (after python -m data.generate)
"""
from __future__ import annotations

import json
import os

from app.graph.base import GraphStore
from app.graph.factory import get_store
from app.schema import Report

HERE = os.path.dirname(__file__)
REPORTS_PATH = os.path.join(HERE, "reports.json")


def load_seed(store: GraphStore, reset: bool = True) -> int:
    """Write the generated seed into a store. Reusable by the CLI and by the
    server's startup auto-seed (needed for the in-memory NetworkX fallback,
    whose graph would otherwise be empty in the uvicorn process)."""
    if not os.path.exists(REPORTS_PATH):
        raise FileNotFoundError("reports.json missing — run `python -m data.generate` first.")
    with open(REPORTS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    if reset:
        store.reset()
    for d in raw:
        store.write_report(Report(**d))
    return len(raw)


def main() -> None:
    store = get_store()
    try:
        count = load_seed(store)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc))

    rings = store.detect_rings()
    print(f"Seeded {count} reports into {type(store).__name__}.")
    print(f"Detected {len(rings)} ring(s):")
    for r in rings:
        kp = r.top_node.value if r.top_node else "—"
        print(f"  {r.ring_id}: {r.report_count} reports, districts={r.districts}, kingpin={kp}")


if __name__ == "__main__":
    main()

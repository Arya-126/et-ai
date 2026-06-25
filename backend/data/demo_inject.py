"""Live demo injection. Posts the 5 held-back reports through POST /report so
the graph visibly GROWS on stage — "Lakshmi" reports and Ring A lights up larger.

Run (with the API up): python -m data.demo_inject
Optional: python -m data.demo_inject --url http://localhost:8000 --delay 2
"""
from __future__ import annotations

import argparse
import json
import os
import time

import requests

HERE = os.path.dirname(__file__)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--delay", type=float, default=2.0)
    args = ap.parse_args()

    path = os.path.join(HERE, "holdback.json")
    if not os.path.exists(path):
        raise SystemExit("holdback.json missing — run `python -m data.generate` first.")

    with open(path, encoding="utf-8") as f:
        holdback = json.load(f)

    for d in holdback:
        payload = {
            "raw_text": d["raw_text"],
            "channel": d.get("channel", "whatsapp"),
            "reporter_id": d.get("reporter_id"),
            "district": d.get("district"),
        }
        resp = requests.post(f"{args.url}/report", json=payload, timeout=60)
        resp.raise_for_status()
        r = resp.json()
        print(f"[{r.get('reporter_id')}] {r['verdict']} "
              f"({r.get('scam_type')}, conf={r.get('confidence')}) "
              f"upi={r.get('upi_id')}")
        time.sleep(args.delay)

    print("\nDemo injection complete — refresh the dashboard and click 'Detect Rings'.")


if __name__ == "__main__":
    main()

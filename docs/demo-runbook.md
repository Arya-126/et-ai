# Demo Runbook (rehearse 5×)

The demo decides ~50% of the score. This is the exact sequence. Total ~3 minutes.

## Pre-flight (before you present)

```bash
# Terminal 1 — backend (choose ONE graph backend)
cd backend && . .venv/Scripts/activate
#   Neo4j path:    docker compose up -d   (wait ~20s)   then GRAPH_BACKEND=neo4j
#   Fallback path: set GRAPH_BACKEND=networkx in .env  (zero infra)
python -m data.generate          # fresh, deterministic dataset
python -m data.seed              # only needed for the Neo4j path (networkx auto-seeds)
uvicorn app.main:app --port 8000

# Terminal 2 + 3 — front ends
cd citizen-app  && npm run dev    # :5173
cd le-dashboard && npm run dev    # :5174
```

Open **two browser windows side by side**: citizen-app (phone-sized) on the left,
le-dashboard (full screen) on the right. Have a 4th terminal ready in `backend/`
for the live injection.

Sanity check: `curl localhost:8000/health` → `status: ok`. On the dashboard, click
**Detect Rings** once to confirm 3 rings appear, then refresh (⟳) to reset visuals.

## The script

1. **Narrator (left/citizen):** "Meet Lakshmi, a retired teacher in Bengaluru. Her
   phone rings — a man claiming to be CBI says her Aadhaar is linked to money
   laundering and orders her to stay on a video call."

2. **Click the `📞 CBI 'digital arrest'` chip** in Fraud Shield.
   → Instant **HIGH RISK — Digital Arrest Scam**, red flags, "CBI never arrests
   over a video call. Do not transfer money. Report to 1930."
   *Beat:* "In two seconds, she's protected. But here's what the judges came for."

3. **Cut to the right (dashboard).** In the 4th terminal:
   ```bash
   python -m data.demo_inject
   ```
   Click **⟳ refresh** on the dashboard. "Her report — and four like it this week —
   just dropped onto the national fraud graph."

4. **Click `🔍 Detect Rings`.** The graph lights into colored communities.
   "Louvain community detection just found that these 24 reports across three
   districts are **one operation**."

5. **Click the top ring (`ring-…`).** Camera flies to it; the **KingpinCard** shows
   `★ digitalarrest.a@okaxis`. "PageRank flags the single UPI handle that ties all
   24 victims together — arrest priority #1."

6. **Click `📄 Generate Intelligence Package`.** A court-ready PDF opens: ring
   summary, prioritized targets, linked reports, synthetic-data disclaimer.

7. **Punchline:** "Rs 1,776 crore was lost in nine months because this loop didn't
   exist between citizens and investigators. We just built it."

## If something breaks

- Dashboard empty / backend error → check `/health`; if Neo4j died, set
  `GRAPH_BACKEND=networkx` and restart uvicorn (auto-seeds).
- Verdict slow or odd → Ollama is optional; the rule layer carries the verdict.
- Anything at all → **play the pre-recorded demo video** (record it by hour 32).

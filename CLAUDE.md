# CLAUDE.md — source of truth for the build

Monorepo for ET AI Hackathon 2026 PS6. **All five components** are built and connected
in one platform: Citizen Fraud Shield (multi-channel, 12 languages) · Digital Arrest
Detection & Alerting · Counterfeit Currency CV · Fraud Network Graph Intelligence ·
Geospatial Crime Pattern Intelligence. Every citizen report feeds the graph, the map,
and the alert system in real time.

## Hard rules (do not violate)
- **The `Report` schema is the contract.** It lives in `backend/app/schema.py`. New fields are added as optional/non-breaking. Everything codes against it.
- **The `GraphStore` ABC is the seam.** Both Neo4j and NetworkX implement it. Frontends and the PDF never import a concrete store — only the factory.
- **Don't let the classifier over-fire.** Benign inputs must never read `HIGH RISK`. `tests/test_rules_false_positive.py` guards this.
- **Graph: two GDS algorithms only** — Louvain (rings) + PageRank (kingpin).
- **Resilience everywhere:** Neo4j→NetworkX, Ollama→rules, CNN→features-only, OSM tiles→SVG map. No live dependency can hard-fail the demo.
- **All synthetic data is disclosed** (`docs/synthetic-disclosure.md`).

## Locked schema
`Report`: report_id, raw_text, channel, claimed_authority, phone, upi_id, account_no, device_hint, reporter_id, district, timestamp, verdict, scam_type, confidence, red_flags[], advice, matched_script_id.

Graph nodes: `Report, PhoneNumber, UPI, Account, Device, ScamScript, Reporter`.
Graph edges: `REPORTED_BY, USED_NUMBER, PAID_TO, FROM_DEVICE, MATCHES_SCRIPT`.
(District is a Report *attribute*, not a node — connecting it would cluster every
report in a city into a false ring.)

## Components → code map
- Citizen Shield (multi-channel/i18n): `platform/src/pages/Shield.jsx`, `data/i18n.py`, `routers/report.py`
- Digital Arrest detection + alerting: `agents/classifier.py`, `rules.py` (spoof sigs), `agents/alerting.py`, `routers/alerts.py`
- Counterfeit Currency CV: `cv/` (generate_notes, model, train, features, infer), `routers/currency.py`
- Fraud Network Graph: `graph/*`, `agents/graph_linker.py`, `agents/package.py`, `routers/{graph,package}.py`
- Geospatial: `data/geo.py`, `routers/geo.py`, `platform/src/pages/CrimeMap.jsx`

## Run commands
- Build unified platform (one-time): `cd platform && npm i && npm run build`
- Generate data: `python -m data.generate`
- Train currency CNN (one-time): `python -m cv.generate_notes && python -m cv.train`
- Seed graph: `python -m data.seed`
- Run everything (platform + API at :8000): `uvicorn app.main:app --reload --port 8000`
- Platform dev (HMR, :5175): `cd platform && npm run dev`
- Tests: `pytest`
- Demo injection: `python -m data.demo_inject`

The single `platform/` app (Home + Citizen Shield + Command Dashboard) is the primary
front end, served by FastAPI from `platform/dist`. `citizen-app/` and `le-dashboard/`
remain as standalone variants.

## Env (`backend/.env`, see `.env.example`)
- `GRAPH_BACKEND=neo4j|networkx`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3.1:8b`
- `NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD`

## Team ownership
- Arya — graph backend (`app/graph/*`, GDS, `agents/graph_linker.py`, `agents/package.py`)
- B — citizen-app + `agents/classifier.py` prompt
- C — le-dashboard + `reporting/pdf.py`
- D — `data/*` (generator, scam scripts), deck, demo direction

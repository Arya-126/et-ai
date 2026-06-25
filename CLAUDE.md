# CLAUDE.md — source of truth for the build

Monorepo for ET AI Hackathon 2026 PS6. Two connected components: Citizen Fraud Shield → Fraud Network Graph Intelligence.

## Hard rules (do not violate)
- **Two connected components, not five.** Digital-arrest detection is folded into the classifier. Counterfeit CV + geospatial are future-scope slides only — zero build.
- **The `Report` schema is frozen.** It lives in `backend/app/schema.py`. Everything codes against it. Change it only by team agreement.
- **The `GraphStore` ABC is the seam.** Both Neo4j and NetworkX implement it. Frontends and the PDF never import a concrete store — only the factory.
- **Don't let the classifier over-fire.** Benign inputs must never read `HIGH RISK`. `tests/test_rules_false_positive.py` guards this.
- **Two GDS algorithms only:** Louvain (rings) + PageRank (kingpin). No gold-plating.

## Locked schema
`Report`: report_id, raw_text, channel, claimed_authority, phone, upi_id, account_no, device_hint, reporter_id, district, timestamp, verdict, scam_type, confidence, red_flags[], advice, matched_script_id.

Graph nodes: `Report, PhoneNumber, UPI, Account, Device, ScamScript, Reporter`.
Graph edges: `REPORTED_BY, USED_NUMBER, PAID_TO, FROM_DEVICE, MATCHES_SCRIPT`.
(District is a Report *attribute*, not a node — connecting it would cluster every
report in a city into a false ring.)

## Run commands
- Build unified platform (one-time): `cd platform && npm i && npm run build`
- Generate data: `python -m data.generate`
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

# Architecture

## The closed loop (the innovation)

Most teams build the five PS6 sub-components as disconnected silos. We build **two,
connected**: every citizen scam report is simultaneously (a) protection for that
citizen and (b) a new data point in a live fraud-network graph. The same event
that warns Lakshmi also grows the map law enforcement uses to dismantle the ring.

```
   CITIZEN SIDE                                  LAW ENFORCEMENT SIDE
 ┌──────────────────────┐                      ┌────────────────────────────┐
 │ Citizen Fraud Shield │                      │  Command Dashboard         │
 │ (WhatsApp-style chat) │                     │  (force-directed graph)    │
 │  paste → verdict      │                     │  Detect Rings / Kingpin /  │
 │                       │                     │  Intelligence Package      │
 └──────────┬───────────┘                      └─────────────▲──────────────┘
            │ POST /report                          GET /graph │ /rings /package
            ▼                                                  │
 ┌───────────────────────────────────────────────────────────┴───────────┐
 │                 FastAPI  +  LangGraph orchestration                      │
 │                                                                         │
 │   IntakeAgent ──► ClassifierAgent ──► GraphLinkerAgent      PackageAgent │
 │   (regex/        (Ollama few-shot     (MERGE nodes/edges    (GDS + PDF,  │
 │    normalize)     + rule layer)        into GraphStore)      on-demand)  │
 └─────────────────────────────┬───────────────────────────────┬──────────┘
                               ▼                                ▼
                   ┌────────────────────────┐        ┌──────────────────┐
                   │  GraphStore (interface) │        │  Synthetic data  │
                   │  ├─ Neo4j + GDS (primary)│       │  ~200 reports,   │
                   │  └─ NetworkX (fallback) │        │  3 planted rings │
                   └────────────────────────┘        └──────────────────┘
```

## Components

### 1. Citizen Fraud Shield (`citizen-app/`)
WhatsApp-style React chat. Citizen pastes a call transcript / SMS / message; the
backend returns a verdict (`HIGH RISK` / `SUSPICIOUS` / `LIKELY SAFE`), red flags,
advice, and a **call 1930** CTA. Quick-fill example chips make the demo one-click.

### 2. The LangGraph pipeline (`backend/app/agents/`)
A deliberately legible linear graph: `intake → classify → graph_link`, with
`package` as a separate on-demand path.

- **IntakeAgent** — deterministic regex normalization (phone → E.164, UPI handle,
  account, claimed authority). No LLM = fast and predictable graph keys.
- **ClassifierAgent** — Ollama (local, free) JSON-mode few-shot over the
  scam-script library, then a **rule layer** (`rules.py`) boosts confidence on
  hard signals and **caps benign messages** so the tool never false-alarms.
  If Ollama is down, it degrades to a rules-only verdict — never a hard failure.
- **GraphLinkerAgent** — MERGEs the report's entities into the `GraphStore`.
  Shared UPI / account / device nodes are what make rings *form*.
- **PackageAgent** — runs GDS, pulls one ring's subgraph + centrality, renders
  the ReportLab PDF.

### 3. Graph intelligence (`backend/app/graph/`)
One `GraphStore` interface, two interchangeable implementations:

- **Neo4j + GDS** (primary): real `gds.louvain` for rings + `gds.pageRank` for the
  kingpin — the "real graph DB" technical story.
- **NetworkX** (fallback): `python-louvain` + `nx.pagerank`, in-memory, zero infra.

`factory.py` auto-falls-back to NetworkX if Neo4j is unreachable at startup, so a
dead Docker container can never kill the live demo.

**Two algorithms, the whole story:**
- *Louvain* → "these 24 reports across 3 districts are one operation."
- *PageRank* → "this one UPI handle ties them all together — arrest priority #1."

### 4. Command Dashboard (`le-dashboard/`)
`react-force-graph-2d`. Loads `GET /graph`; **Detect Rings** colors Louvain
communities and lists them; selecting a ring flies the camera to it, renders the
**KingpinCard** (top PageRank node + infrastructure), and **Generate Intelligence
Package** opens the court-ready PDF.

## Data model

**Nodes:** `Report, PhoneNumber, UPI, Account, Device, ScamScript, Reporter`
**Edges:** `REPORTED_BY, USED_NUMBER, PAID_TO, FROM_DEVICE, MATCHES_SCRIPT`

> District is a Report *attribute*, not a node. (A District node would be a hub
> linking every unrelated report in a city — a false ring. We learned this the
> hard way: with District as a node, noise clustered into 14 fake rings; removing
> it left exactly the 3 planted rings.)

Node id convention `Label:value` (e.g. `UPI:digitalarrest.a@okaxis`) makes MERGE
and dedup trivial and keeps ids stable across the two backends.

## API surface (all components, one backend)

| Method | Path | Component | Purpose |
|---|---|---|---|
| POST | `/report` | 1,2,5 | Citizen message → enriched `Report` (verdict, localized advice, alert) |
| POST | `/report/complaint` | 5 | NCRB/cybercrime.gov.in complaint PDF from a report |
| GET | `/languages` | 5 | Supported languages for the Shield selector |
| GET | `/alerts` · `/alerts/{id}/pdf` | 1 | Generated MHA/telecom alerts + alert PDF |
| POST | `/currency/scan` | 2 | Note image → genuine/counterfeit + feature breakdown |
| GET | `/currency/samples` · `/samples/{id}` | 2 | Demo sample notes |
| GET | `/graph` · `/rings` | 4 | Fraud graph + community colors; detected rings + kingpin |
| GET | `/package/{ring_id}` · `/pdf` | 4 | Ring subgraph + PageRank + court-ready PDF |
| GET | `/geo` | 4(geo) | Complaint hotspots, patrol priority, seizures |
| GET | `/health` | — | Status + component readiness (`graph_backend`, `llm_up`, `currency_cnn`, `spa_built`) |

Everything else is served as the **platform SPA** (catch-all → `index.html`).

## Resilience (every external dependency has a fallback)

- **Neo4j down / no Docker** → auto-fallback to NetworkX, identical behavior.
- **Ollama down / no GPU** → classifier degrades to the deterministic rule layer.
- **Currency CNN weights missing** → `infer` degrades to OpenCV features-only.
- **OSM tiles blocked** → Crime Map falls back to an offline SVG India plot.
- **In-memory backend** → the server auto-seeds `reports.json` on startup.

## Deployment

Single `Dockerfile` (multi-stage: Node build → Python runtime) bakes the demo data
and trained currency CNN, then serves the SPA + API on `:8000`. `docker compose up
app` runs it standalone (NetworkX); the `neo4j` compose profile adds the GDS graph
DB. CI (GitHub Actions) runs the backend tests + a production platform build.

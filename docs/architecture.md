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

## API surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/report` | Citizen submits a message → enriched `Report` (verdict + entities) |
| GET | `/graph` | Full graph + community colors for the force viz |
| GET | `/rings` | Detected rings (Louvain) with kingpin per ring |
| GET | `/package/{ring_id}` | Ring subgraph + PageRank centrality + PDF url |
| GET | `/package/{ring_id}/pdf` | The rendered intelligence package PDF |
| GET | `/health` | Backend status, active graph backend, LLM reachability |

## Resilience (live-demo insurance)

- **No Docker / Neo4j down** → auto-fallback to NetworkX, identical behavior.
- **In-memory backend** → the server auto-seeds `reports.json` on startup (the CLI
  seed runs in a different process).
- **Ollama down / no GPU** → classifier degrades to the deterministic rule layer.
- **Live demo fails entirely** → pre-recorded demo video (deliverable).

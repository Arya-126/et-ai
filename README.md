# Fraud Network Intelligence + Citizen Fraud Shield

> A scared citizen's WhatsApp message becomes the data that maps a criminal fraud network — in real time.

**ET AI Hackathon 2026 — Problem Statement 6.** All **five** components, built and
connected in one platform (one URL, one backend):

| # | Component | In the platform |
|---|---|---|
| 1 | **Citizen Fraud Shield** (multi-channel) | WhatsApp + IVR chat, instant verdicts, **12 regional languages**, guided 1930/NCRB complaint PDF — `/shield` |
| 2 | **Digital Arrest Detection & Alerting** | classifier + spoof signatures; auto-generates **MHA/I4C + telecom alerts** before transfer — `/shield`, alerts on `/command` |
| 3 | **Counterfeit Currency Identification** | **PyTorch CNN + OpenCV** feature breakdown (microprint, thread, UV, serial) — `/currency` |
| 4 | **Fraud Network Graph Intelligence** | Neo4j+GDS/NetworkX, Louvain rings + PageRank kingpin, court-ready PDF — `/command` |
| 5 | **Geospatial Crime Pattern Intelligence** | Leaflet command-centre map: hotspots, seizures, patrol priority — `/map` |

The innovation is the **closed loop**: every citizen report feeds the graph, the map,
and the alert system in real time.

## The loop

```
Citizen pastes a scam message  ──► instant verdict ("HIGH RISK — Digital Arrest Scam")
        │
        └► POST /report ──► LangGraph pipeline ──► fraud graph grows
                                                      │
        Law-enforcement dashboard ◄── GET /graph ◄────┘
              │  "Detect Rings"  ──► Louvain lights up a 40-node ring across 3 districts
              │  PageRank        ──► flags the central mule account (arrest priority #1)
              └► "Generate Intelligence Package" ──► court-ready PDF
```

## Architecture

```
   CITIZEN SIDE                              LAW ENFORCEMENT SIDE
 ┌─────────────────────┐                  ┌──────────────────────────┐
 │ Fraud Shield (chat) │                  │ Command Dashboard (React)│
 │ paste → verdict     │                  │ force-directed ring graph│
 └──────────┬──────────┘                  └────────────▲─────────────┘
            │ POST /report                              │ GET /graph, /package
            ▼                                           │
 ┌──────────────────────────────────────────────────────────────────┐
 │            FastAPI  +  LangGraph orchestration                     │
 │  IntakeAgent → ClassifierAgent → GraphLinkerAgent → PackageAgent   │
 │    normalize       Ollama (local)     write graph      ReportLab   │
 └───────────────┬───────────────────────────┬──────────────────────┘
                 ▼                            ▼
        ┌──────────────────┐        ┌──────────────────┐
        │  GraphStore      │        │  Synthetic data  │
        │  Neo4j+GDS  OR   │        │  ~200 reports,   │
        │  NetworkX (fallbk)│       │  planted rings   │
        └──────────────────┘        └──────────────────┘
```

## Stack

| Layer | Choice |
|---|---|
| Orchestration | LangGraph |
| API | FastAPI |
| LLM | **Ollama (local, free)** — `llama3.1:8b` default |
| Graph DB | **Neo4j + GDS** (primary) / **NetworkX** (fallback) — one interface |
| Graph viz | react-force-graph |
| Front end | **One unified platform** (`platform/`) — React + Tailwind + router (Vite). Served by the backend. |
| PDF | ReportLab (pure Python) |

## Quick start (one platform, one URL)

Everything — Home, Citizen Shield, and Command Dashboard — runs as a single app
served by the FastAPI backend at **http://localhost:8000**.

```bash
# 1. (optional) Neo4j — primary graph path
docker compose up -d                 # bolt://localhost:7687

# 2. Local LLM
ollama pull llama3.2:3b

# 3. Build the unified platform (one-time; outputs platform/dist)
cd platform && npm i && npm run build

# 4. Backend (serves the platform + the API)
cd ../backend
python -m venv .venv && . .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# torch is CPU-only via its own index (see requirements.txt header):
#   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
cp ../.env.example .env               # edit GRAPH_BACKEND / OLLAMA_MODEL if needed
python -m data.generate               # writes data/reports.json (~200, planted rings)
python -m cv.generate_notes && python -m cv.train   # currency CNN (one-time, ~2 min CPU)
python -m data.seed                   # Neo4j path only; the in-memory path auto-seeds
uvicorn app.main:app --reload --port 8000

# open http://localhost:8000  ->  Home / Citizen Shield / Command Dashboard
```

**Front-end dev (HMR):** `cd platform && npm run dev` → http://localhost:5175
(Vite proxies the API to :8000). The standalone `citizen-app/` and `le-dashboard/`
remain in the repo for split deployments, but the **unified `platform/` is the
primary entry point**.

**No Docker?** Set `GRAPH_BACKEND=networkx` in `.env` — everything else is identical. The backend also auto-falls-back to NetworkX if it can't reach Neo4j at startup.

> **Neo4j + GDS is verified.** Real Neo4j 5.20 + GDS 2.6.9 reproduces the NetworkX
> ring detection exactly (Louvain finds the 3 planted rings; PageRank flags the
> shared mule account/UPI). See [docs/neo4j-gds-verification.md](docs/neo4j-gds-verification.md) for the actual output.
> If the GDS plugin is slow to auto-download on first `docker compose up` (the
> `graphdatascience.ninja` CDN blocks some clients), pre-download the 60 MB jar once
> and mount it into `/var/lib/neo4j/plugins` — details in that doc.

**No GPU?** Use a smaller model: `ollama pull llama3.2:3b` then set `OLLAMA_MODEL=llama3.2:3b`. The classifier still works because `rules.py` carries the hard signals.

### LLM performance note (read before the demo)

The classifier calls a **local** Ollama model and then a deterministic rule layer.
On a **GPU** machine `llama3.2:3b` returns a verdict in ~1–3s and its output is
used directly. On a **CPU-only** machine a 3B model can take 20–40s per
classification — too slow for a live citizen request — so `OLLAMA_TIMEOUT` (default
**3s** in `.env`) bounds the wait and the request **falls back to the instant rule
layer**, which is accurate on the demo scripts. Net: the citizen experience is
always fast; the LLM adds nuance only when the hardware can deliver it quickly.
Verified: `llama3.2:3b` classifies the scam/benign suite correctly in isolation —
the only variable is per-box latency. For a snappy live demo on a slow laptop,
leaving it to fall back to rules is the safe choice; on a GPU box raise the timeout.

## Demo

With the platform open at http://localhost:8000:

1. **Citizen Shield** tab → paste a scam (or tap the *CBI 'digital arrest'* chip) →
   instant **HIGH RISK** verdict + advice + call-1930. The report joins the graph.
2. Optionally inject the held-back reports so the graph visibly grows on stage:
   ```bash
   cd backend && python -m data.demo_inject     # "Lakshmi" + 4 held-back reports
   ```
3. **Command Dashboard** tab → **⟳ refresh** → **Detect Rings** (3 rings light up) →
   click the top ring → kingpin highlighted → **Generate Intelligence Package** (PDF).

Full rehearsable script: [docs/demo-runbook.md](docs/demo-runbook.md).
See also [docs/architecture.md](docs/architecture.md) and [docs/synthetic-disclosure.md](docs/synthetic-disclosure.md).

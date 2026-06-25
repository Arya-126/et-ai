"""FastAPI app. Wires CORS + the three routers and warms the graph store on
startup (which triggers the Neo4j->NetworkX auto-fallback early, not mid-demo).
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.graph.factory import get_store
from app.graph.networkx_store import NetworkXStore
from app.llm import is_up as llm_is_up
from app.llm import warmup as llm_warmup
from app.routers import alerts, currency, geo, graph, package, report

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

app = FastAPI(title="Fraud Network Intelligence + Citizen Fraud Shield", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report.router)
app.include_router(graph.router)
app.include_router(package.router)
app.include_router(alerts.router)
app.include_router(geo.router)
app.include_router(currency.router)


@app.on_event("startup")
def _startup() -> None:
    store = get_store()  # triggers backend selection + fallback now
    log.info("Graph store ready: %s", type(store).__name__)
    # In-memory backend lives only in this process, so auto-load the seed here
    # (the CLI `data.seed` would populate a different process). Neo4j persists,
    # so it is seeded once via the CLI and left alone.
    if isinstance(store, NetworkXStore) and not store.g.number_of_nodes():
        try:
            from data.seed import load_seed

            n = load_seed(store)
            log.info("Auto-seeded %d reports into in-memory graph.", n)
        except FileNotFoundError:
            log.warning("No seed found — run `python -m data.generate` for demo data.")
    if llm_is_up():
        log.info("Ollama reachable (model=%s) — warming up…", settings.ollama_model)
        log.info("LLM warmup ok: %s", llm_warmup())
    else:
        log.info("Ollama not reachable — classifier will use the rule layer.")


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {
        "status": "ok",
        "graph_backend": type(get_store()).__name__,
        "llm_up": llm_is_up(),
        "llm_model": settings.ollama_model,
    }


# --------------------------------------------------------------------------
# Serve the unified platform SPA (one URL for everything). Mounted AFTER the API
# routers so /report, /graph, /rings, /package, /health always take precedence;
# the catch-all returns index.html so client-side routes (/shield, /command) and
# deep-link refreshes work. If the SPA hasn't been built yet, this is skipped and
# the backend runs API-only.
# --------------------------------------------------------------------------
_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "platform", "dist"
)


def _mount_spa() -> None:
    index = os.path.join(_DIST, "index.html")
    if not os.path.exists(index):
        log.warning("Platform SPA not built (%s missing). Run `cd platform && npm run build`.", index)
        return
    assets = os.path.join(_DIST, "assets")
    if os.path.isdir(assets):
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        # Serve a real static file if it exists (favicon, etc.), else the SPA shell.
        candidate = os.path.join(_DIST, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(index)

    log.info("Serving unified platform SPA from %s", _DIST)


_mount_spa()

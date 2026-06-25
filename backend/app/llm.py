"""Thin Ollama wrapper. Local, free, offline. JSON-mode chat with a hard
timeout; raises LLMUnavailable so the classifier can degrade to rules-only
rather than hard-fail on stage.
"""
from __future__ import annotations

import json
import logging

import ollama

from app.config import settings

log = logging.getLogger("llm")


class LLMUnavailable(Exception):
    pass


_client: ollama.Client | None = None


def _get_client() -> ollama.Client:
    global _client
    if _client is None:
        _client = ollama.Client(host=settings.ollama_base_url, timeout=settings.ollama_timeout)
    return _client


def chat_json(system: str, user: str) -> dict:
    """Run a chat completion forced to JSON and parse it. Raises LLMUnavailable
    on any transport/parse error."""
    try:
        resp = _get_client().chat(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            format="json",
            # Cap generation so a slow CPU box can't stall the citizen request;
            # the verdict JSON is short anyway.
            options={"temperature": 0.1, "num_predict": 220},
        )
        content = resp["message"]["content"]
        return json.loads(content)
    except json.JSONDecodeError as exc:
        log.warning("LLM returned non-JSON: %s", exc)
        raise LLMUnavailable("bad json") from exc
    except Exception as exc:  # noqa: BLE001 — Ollama down / model missing / timeout
        log.warning("Ollama unavailable: %s", exc)
        raise LLMUnavailable(str(exc)) from exc


def is_up() -> bool:
    try:
        _get_client().list()
        return True
    except Exception:  # noqa: BLE001
        return False


def warmup() -> bool:
    """Load the model into memory with a tiny inference so the first real
    citizen request isn't slow (cold-start otherwise loads GBs on first hit)."""
    try:
        _get_client().chat(
            model=settings.ollama_model,
            messages=[{"role": "user", "content": "ok"}],
            options={"num_predict": 1},
        )
        return True
    except Exception as exc:  # noqa: BLE001
        log.info("LLM warmup skipped: %s", exc)
        return False

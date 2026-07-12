"""Background auto-refresh — makes DATA_MODE=live genuinely hands-off.

Runs entirely in-process (a daemon thread), no external scheduler, no extra
dependency, no cost: on API startup it immediately pulls fresh data once, then
repeats every `auto_refresh_interval_seconds` (default 1 hour) for as long as the
process runs. This replaces ever needing to type `start_api.bat refresh` manually -
the previous auto-migration work (app.db.session) only kept the DB *schema* healed
automatically; this is what keeps the DB *contents* fresh automatically too.

Every run reuses the exact same ingest -> clean -> validate -> reconcile -> load
pipeline as scripts/hourly_refresh.py, so the double-check reconciliation gate
(docs/04_data_freshness_and_accuracy.md) still protects against a bad pull even
when nobody is watching.
"""
from __future__ import annotations

import threading
import time

from app.cleaning import clean
from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import load_cleaned_into_db
from app.ingestion import run_all

logger = get_logger(__name__)
_started = False
_lock = threading.Lock()


def _refresh_once() -> None:
    try:
        ingested = run_all.run()
        cleaned = clean.run()
        loaded = load_cleaned_into_db()
        logger.info(
            "Auto-refresh complete: ingested=%d cleaned=%d loaded=%s",
            len(ingested), len(cleaned), loaded,
        )
    except Exception as exc:  # noqa: BLE001 - a failed background refresh must never crash the API
        logger.warning("Auto-refresh failed (%s); keeping previously loaded data.", exc)


def _loop() -> None:
    settings = get_settings()
    while True:
        _refresh_once()
        time.sleep(max(60, settings.auto_refresh_interval_seconds))


def start_background_refresh() -> None:
    """Idempotent - safe to call from the FastAPI startup hook even across
    uvicorn --reload restarts without spawning duplicate threads within one process."""
    global _started
    settings = get_settings()
    if not settings.auto_refresh_enabled:
        logger.info("Auto-refresh disabled (AUTO_REFRESH_ENABLED=false).")
        return
    with _lock:
        if _started:
            return
        _started = True
    thread = threading.Thread(target=_loop, name="auto-refresh", daemon=True)
    thread.start()
    logger.info(
        "Background auto-refresh started (every %ds).", settings.auto_refresh_interval_seconds
    )

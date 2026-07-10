"""Azure Function — Timer Trigger: hourly ingestion + double-check reconciliation.

function.json (sibling file) defines schedule "0 0 * * * *" (top of every hour).
This wraps scripts/hourly_refresh.py so local and cloud runs share the exact same
ingest -> clean -> validate -> reconcile -> load logic (see docs/04_data_freshness_and_accuracy.md).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import azure.functions as func

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "api"))


def main(mytimer: func.TimerRequest) -> None:
    from app.cleaning import clean
    from app.db.session import load_cleaned_into_db
    from app.ingestion import run_all

    logging.info("Hourly ingestion trigger fired.")
    ingested = run_all.run()
    cleaned = clean.run()
    loaded = load_cleaned_into_db()
    logging.info("Hourly ingestion complete: ingested=%d cleaned=%d loaded=%s",
                 len(ingested), len(cleaned), loaded)

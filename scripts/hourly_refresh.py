"""
hourly_refresh.py — the single entrypoint the hourly scheduler calls.

Local cron example (every hour, on the hour):
    0 * * * * cd /path/to/project/python && /usr/bin/python3 ../scripts/hourly_refresh.py >> ../logs/hourly.log 2>&1

Azure production: the same three-step call is wrapped by an Azure Function timer
trigger — see azure/functions/hourly_ingestion (schedule "0 0 * * * *").

Every run: ingest -> clean -> validate + double-check reconcile -> load.
Nothing is promoted to the serving DB unless it passes BOTH the schema/range gate
and the cross-run reconciliation gate (see docs/04_data_freshness_and_accuracy.md).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.cleaning import clean  # noqa: E402
from app.core.logging import get_logger  # noqa: E402
from app.db.session import load_cleaned_into_db  # noqa: E402
from app.ingestion import run_all  # noqa: E402

logger = get_logger("hourly_refresh")


def main() -> None:
    start = time.time()
    logger.info("=== Hourly refresh started ===")

    ingested = run_all.run()
    logger.info("Ingestion step: %d file(s)", len(ingested))

    cleaned = clean.run()
    logger.info("Cleaning step: %d file(s)", len(cleaned))

    loaded = load_cleaned_into_db()
    logger.info("Load step (post double-check): %s", loaded)

    logger.info("=== Hourly refresh finished in %.1fs ===", time.time() - start)


if __name__ == "__main__":
    main()

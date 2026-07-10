"""
Ingestion orchestrator.

Usage:
    python -m app.ingestion.run_all

Behavior:
    - data_mode == "live": attempts to pull from real public sources (app.ingestion.sources).
      On any failure (no network, schema change, timeout), logs a warning and falls back
      to the bundled sample dataset so downstream stages never break.
    - data_mode == "sample": copies the pre-generated sample dataset straight into data/raw,
      tagged with its source file name, so it flows through the exact same
      raw -> cleaned -> validated pipeline as real data would.
"""
from __future__ import annotations

import shutil
from datetime import datetime, timezone

import pandas as pd

from app.core.config import get_settings
from app.core.logging import get_logger
from app.ingestion import sources

logger = get_logger(__name__)


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run() -> list[str]:
    settings = get_settings()
    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    # Clear stale raw files from previous runs first. Without this, old and new files
    # for the same dataset can coexist in data/raw, and app.cleaning.clean's glob-order
    # iteration isn't guaranteed to pick the newest one when writing data/cleaned/*.csv.
    for stale in settings.raw_dir.glob("*.csv"):
        stale.unlink()

    if settings.data_mode == "live":
        try:
            # Filename must contain "co2energy" (no separators) so app.cleaning.clean's
            # filename-based cleaner lookup routes it to clean_co2_energy — the previous
            # "owid_co2_..." / "owid_energy_..." split-file naming didn't match anything
            # and was silently skipped by the cleaning step (data never left data/raw).
            merged = sources.fetch_and_merge_co2_energy()
            out1 = settings.raw_dir / f"owid_co2_energy_dach_{_stamp()}.csv"
            merged.to_csv(out1, index=False)
            written += [str(out1)]
            logger.info("Live ingestion succeeded: %s", written)
            return written
        except Exception as exc:  # noqa: BLE001 - deliberate broad fallback
            logger.warning("Live ingestion failed (%s). Falling back to sample data.", exc)

    # Sample mode / fallback
    for f in settings.sample_dir.glob("*.csv"):
        dest = settings.raw_dir / f.name
        shutil.copy(f, dest)
        written.append(str(dest))
    logger.info("Sample ingestion complete: %s", written)
    return written


if __name__ == "__main__":
    files = run()
    print(f"Ingested {len(files)} file(s):")
    for f in files:
        print(f"  - {f}")

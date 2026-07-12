"""One-off, in-place schema migration: makes the secondary co2_energy columns
(co2_per_capita_t, fossil_share_pct, nuclear_share_pct, electricity_generation_twh,
electricity_price_eur_mwh) nullable, matching the Optional fields added to
app.validation.schemas.CO2EnergyRecord and app.db.models.CO2Energy.

Uses SQLite's standard "recreate table" pattern (ALTER COLUMN isn't supported
directly). Runs as a separate short-lived connection to the same database file, so
it does NOT require stopping uvicorn or the R dashboard first - unlike deleting the
.db file outright, which needs an exclusive OS-level lock Windows won't grant while
another process has the file open.

Usage (from the api/ folder, while the API keeps running in another window):
    python scripts/migrate_nullable_columns.py
"""
from __future__ import annotations

from sqlalchemy import text

from app.core.logging import get_logger
from app.db.session import engine

logger = get_logger(__name__)

NEW_COLUMNS_SQL = """
CREATE TABLE co2_energy_migrated (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code VARCHAR(2) NOT NULL,
    year INTEGER NOT NULL,
    co2_emissions_mt FLOAT NOT NULL,
    renewable_share_pct FLOAT NOT NULL,
    co2_per_capita_t FLOAT,
    fossil_share_pct FLOAT,
    nuclear_share_pct FLOAT,
    electricity_generation_twh FLOAT,
    electricity_price_eur_mwh FLOAT,
    data_quality VARCHAR(20)
)
"""


def run() -> None:
    with engine.begin() as conn:
        # Give this connection up to 30s to wait its turn if uvicorn's connection is
        # mid-read at the same instant, instead of failing immediately with
        # "database is locked" - this is what makes running the migration alongside
        # the still-running API/dashboard reliable.
        conn.execute(text("PRAGMA busy_timeout = 30000"))
        existing = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='co2_energy'")
        ).fetchone()
        if existing is None:
            logger.info("co2_energy table doesn't exist yet - nothing to migrate, "
                        "it will be created with the correct nullable schema on first load.")
            return

        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(co2_energy)")).fetchall()]
        # electricity_price_eur_mwh being NOT NULL is what we're fixing; if the table
        # already accepts nulls there, a previous run of this script already migrated it.
        already_nullable = conn.execute(
            text("SELECT sql FROM sqlite_master WHERE type='table' AND name='co2_energy'")
        ).scalar()
        if already_nullable and "electricity_price_eur_mwh FLOAT NOT NULL" not in already_nullable.replace("\n", " "):
            logger.info("co2_energy already has a nullable schema - nothing to do.")
            return

        logger.info("Migrating co2_energy to a nullable-secondary-columns schema in place...")
        conn.execute(text(NEW_COLUMNS_SQL))
        common_cols = ", ".join(c for c in cols if c != "id")
        conn.execute(text(
            f"INSERT INTO co2_energy_migrated ({common_cols}) SELECT {common_cols} FROM co2_energy"
        ))
        conn.execute(text("DROP TABLE co2_energy"))
        conn.execute(text("ALTER TABLE co2_energy_migrated RENAME TO co2_energy"))
        logger.info("Migration complete. co2_energy now accepts NULLs in secondary columns.")


if __name__ == "__main__":
    run()

"""Database engine/session management + load routine that pushes validated
cleaned CSVs into the serving database."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import Float, Integer, String, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.models import Base, CO2Energy, CompanyESG, RegionalClimateRisk
from app.validation.checks import validate_dataframe
from app.validation.reconciliation import reconcile
from app.validation.schemas import CO2EnergyRecord, CompanyESGRecord, RegionalClimateRiskRecord

logger = get_logger(__name__)

settings = get_settings()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# --- Auto-migration: keeps the on-disk schema in sync with app.db.models automatically,
# every time init_db() runs (which happens on every API startup - see app.api.main's
# startup hook - and on every uvicorn --reload auto-restart). This is what lets future
# schema fixes (like the electricity_price_eur_mwh nullability bug) apply themselves
# with no manual migration script or human action required; see docs/09_deployment_guide.md.
def _sqlite_coltype(col) -> str:
    if isinstance(col.type, Integer):
        return "INTEGER"
    if isinstance(col.type, Float):
        return "FLOAT"
    if isinstance(col.type, String):
        length = getattr(col.type, "length", None)
        return f"VARCHAR({length})" if length else "VARCHAR"
    return "TEXT"


def _table_needs_recreate(conn, table) -> bool:
    info = conn.execute(text(f"PRAGMA table_info({table.name})")).fetchall()
    if not info:
        return False  # table doesn't exist yet - create_all() handles that case
    actual_notnull = {row[1]: bool(row[3]) for row in info}  # column name -> NOT NULL flag
    for col in table.columns:
        if col.name not in actual_notnull:
            return True  # a model column is missing from the real table
        expected_notnull = not col.nullable and not col.primary_key
        if actual_notnull[col.name] != expected_notnull:
            return True  # nullability drifted (e.g. a field we made Optional)
    return False


def _recreate_table_in_place(conn, table) -> None:
    tmp_name = f"{table.name}__automigrate"
    col_defs = []
    for col in table.columns:
        parts = [col.name, _sqlite_coltype(col)]
        if col.primary_key:
            parts.append("PRIMARY KEY AUTOINCREMENT")
        elif not col.nullable:
            parts.append("NOT NULL")
        col_defs.append(" ".join(parts))
    conn.execute(text(f"CREATE TABLE {tmp_name} ({', '.join(col_defs)})"))

    existing_cols = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table.name})")).fetchall()}
    common = [c.name for c in table.columns if c.name in existing_cols]
    common_sql = ", ".join(common)
    conn.execute(text(f"INSERT INTO {tmp_name} ({common_sql}) SELECT {common_sql} FROM {table.name}"))
    conn.execute(text(f"DROP TABLE {table.name}"))
    conn.execute(text(f"ALTER TABLE {tmp_name} RENAME TO {table.name}"))


def ensure_schema_up_to_date() -> None:
    """Creates any missing tables, then auto-heals column drift (missing columns or a
    nullable/NOT NULL mismatch) on existing tables in place. Safe to call on every
    startup - a no-op when the schema already matches app.db.models."""
    Base.metadata.create_all(bind=engine)
    if "sqlite" not in settings.database_url:
        return  # auto-recreate strategy below is SQLite-specific; Azure SQL uses managed migrations
    with engine.begin() as conn:
        conn.execute(text("PRAGMA busy_timeout = 30000"))
        for table in Base.metadata.sorted_tables:
            try:
                if _table_needs_recreate(conn, table):
                    logger.info("Auto-migrating '%s' to match the current model schema...", table.name)
                    _recreate_table_in_place(conn, table)
                    logger.info("Auto-migration of '%s' complete.", table.name)
            except Exception as exc:  # noqa: BLE001 - never let a migration hiccup block startup
                logger.warning("Auto-migration check failed for '%s': %s (continuing)", table.name, exc)


def init_db() -> None:
    ensure_schema_up_to_date()


TABLE_MAP = {
    "co2_energy": (CO2EnergyRecord, CO2Energy),
    "regional_climate_risk": (RegionalClimateRiskRecord, RegionalClimateRisk),
    "company_esg": (CompanyESGRecord, CompanyESG),
}


def load_cleaned_into_db() -> dict[str, int]:
    """Reads data/cleaned/*.csv, validates, and upserts into the serving DB."""
    init_db()
    loaded: dict[str, int] = {}
    with SessionLocal() as session:  # type: Session
        for key, (schema, model) in TABLE_MAP.items():
            path = settings.cleaned_dir / f"{key}.csv"
            if not path.exists():
                logger.warning("No cleaned file for %s at %s, skipping", key, path)
                continue
            df = pd.read_csv(path)
            valid_records, report = validate_dataframe(df, schema, key)
            if not report.passed:
                logger.error("%s failed quality gate, NOT loading into DB", key)
                continue

            # Double-check gate: reconcile against what's already in the DB before overwriting.
            existing_rows = session.query(model).all()
            previous_df = pd.DataFrame([
                {c.name: getattr(r, c.name) for c in model.__table__.columns} for r in existing_rows
            ]) if existing_rows else None
            new_df = pd.DataFrame(valid_records)
            safe_df, recon_report = reconcile(key, new_df, previous_df)
            if not recon_report.clean:
                logger.warning(
                    "%s: %d anomalous row(s) withheld from promotion this run",
                    key, recon_report.anomaly_count,
                )
            safe_records = safe_df.to_dict(orient="records")

            session.query(model).delete()
            session.bulk_insert_mappings(model, safe_records)
            session.commit()
            loaded[key] = len(safe_records)
            logger.info("Loaded %d rows into %s (%d withheld by double-check)",
                        len(safe_records), key, len(valid_records) - len(safe_records))
    return loaded


if __name__ == "__main__":
    result = load_cleaned_into_db()
    print(result)

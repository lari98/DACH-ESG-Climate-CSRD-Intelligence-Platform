"""Database engine/session management + load routine that pushes validated
cleaned CSVs into the serving database."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine
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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


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

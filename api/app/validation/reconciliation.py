"""Cross-run reconciliation ("double-check") gate.

Compares a freshly cleaned dataset against the last snapshot already loaded into
the serving database. Any row whose key numeric fields moved by more than the
configured tolerance is flagged as an anomaly and withheld from promotion, so a
bad pull (truncated file, source outage, unit mix-up) can never silently
overwrite good data. This is what "double-checking" data means in a pipeline —
not a second manual look, but a second automated, auditable gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.core.logging import get_logger

logger = get_logger(__name__)

# tolerance = max allowed relative change before a value is flagged as anomalous
TOLERANCE = {
    "co2_energy": 0.15,              # official annual series: should move slowly
    "regional_climate_risk": 0.25,   # model-based scores, a bit more volatile
    "company_esg": 0.30,             # user-submitted, can genuinely jump
}

KEY_COLUMNS = {
    "co2_energy": ["country_code", "year"],
    "regional_climate_risk": ["country_code", "region"],
    "company_esg": ["company_id"],
}

NUMERIC_CHECK_COLUMNS = {
    "co2_energy": ["co2_emissions_mt", "renewable_share_pct"],
    "regional_climate_risk": ["composite_climate_risk_score"],
    "company_esg": ["scope1_tco2e", "scope2_tco2e", "scope3_tco2e"],
}


@dataclass
class ReconciliationReport:
    dataset: str
    rows_compared: int
    anomalies: list[dict] = field(default_factory=list)

    @property
    def anomaly_count(self) -> int:
        return len(self.anomalies)

    @property
    def clean(self) -> bool:
        return self.anomaly_count == 0


def reconcile(dataset: str, new_df: pd.DataFrame, previous_df: pd.DataFrame | None) -> tuple[pd.DataFrame, ReconciliationReport]:
    """Returns (rows_safe_to_promote, report). Flagged rows are dropped from promotion."""
    if previous_df is None or previous_df.empty:
        logger.info("%s: no previous snapshot to reconcile against, promoting all %d rows", dataset, len(new_df))
        return new_df, ReconciliationReport(dataset=dataset, rows_compared=0)

    key_cols = KEY_COLUMNS[dataset]
    check_cols = NUMERIC_CHECK_COLUMNS[dataset]
    tolerance = TOLERANCE[dataset]

    merged = new_df.merge(previous_df, on=key_cols, how="left", suffixes=("_new", "_prev"))
    anomalies: list[dict] = []
    bad_index = set()

    for i, row in merged.iterrows():
        for col in check_cols:
            new_val = row.get(f"{col}_new")
            prev_val = row.get(f"{col}_prev")
            if pd.isna(prev_val) or pd.isna(new_val) or prev_val == 0:
                continue
            rel_change = abs(new_val - prev_val) / abs(prev_val)
            if rel_change > tolerance:
                anomalies.append({
                    "row_key": {k: row[k] for k in key_cols},
                    "column": col,
                    "previous_value": prev_val,
                    "new_value": new_val,
                    "relative_change": round(rel_change, 3),
                    "tolerance": tolerance,
                })
                bad_index.add(i)

    safe_rows = new_df.drop(index=[i for i in bad_index if i in new_df.index], errors="ignore")
    report = ReconciliationReport(dataset=dataset, rows_compared=len(merged), anomalies=anomalies)

    if report.clean:
        logger.info("%s: reconciliation PASSED, no anomalies across %d rows", dataset, report.rows_compared)
    else:
        logger.warning("%s: reconciliation flagged %d anomalies (withheld from promotion)", dataset, report.anomaly_count)
        for a in anomalies[:10]:
            logger.warning("  anomaly: %s", a)

    return safe_rows, report

"""Row-level + dataset-level data quality checks, run between the cleaned layer
and the serving database. Mirrors the checks re-implemented in PySpark for the
Databricks Silver->Gold boundary (see databricks/notebooks/silver)."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
from pydantic import BaseModel, ValidationError

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationReport:
    dataset: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: list[str] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return 0.0 if self.total_rows == 0 else self.valid_rows / self.total_rows

    @property
    def passed(self) -> bool:
        # Data quality gate: at least 95% of rows must validate cleanly.
        return self.pass_rate >= 0.95


def validate_dataframe(df: pd.DataFrame, model: type[BaseModel], dataset_name: str) -> tuple[list[dict], ValidationReport]:
    valid_records: list[dict] = []
    errors: list[str] = []
    for i, row in df.iterrows():
        try:
            # pandas round-trips missing optional values (e.g. electricity price, absent
            # from free live sources) as NaN, not None/absent. Pydantic's numeric
            # constraints (e.g. ge=0) reject NaN even on Optional fields since
            # `float('nan') >= 0` is False, so translate NaN -> None before validating.
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            record = model(**row_dict)
            valid_records.append(record.model_dump())
        except ValidationError as exc:
            errors.append(f"row {i}: {exc.errors()[0]['msg']}")

    report = ValidationReport(
        dataset=dataset_name,
        total_rows=len(df),
        valid_rows=len(valid_records),
        invalid_rows=len(df) - len(valid_records),
        errors=errors[:20],  # cap stored errors
    )
    if report.passed:
        logger.info("%s: PASSED (%.1f%% valid)", dataset_name, report.pass_rate * 100)
    else:
        logger.warning("%s: FAILED quality gate (%.1f%% valid)", dataset_name, report.pass_rate * 100)
    return valid_records, report

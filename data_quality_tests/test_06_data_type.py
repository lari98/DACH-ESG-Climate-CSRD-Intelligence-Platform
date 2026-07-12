"""6. Data-type test — every column that reaches the database must actually validate
against its Pydantic type (int/float/str/Literal), not just "exist"."""
from __future__ import annotations

import pandas as pd

from app.validation.checks import validate_dataframe
from app.validation.schemas import CO2EnergyRecord, CompanyESGRecord, RegionalClimateRiskRecord


def _typecheck(df: pd.DataFrame, model, dataset_name: str):
    _, report = validate_dataframe(df, model, dataset_name)
    assert report.total_rows > 0, f"{dataset_name}: no rows to type-check"
    assert report.passed, (
        f"{dataset_name}: only {report.pass_rate:.1%} of rows match the expected types "
        f"(need >=95%). Sample errors: {report.errors[:5]}"
    )


def test_co2_energy_types(co2_energy_df):
    _typecheck(co2_energy_df, CO2EnergyRecord, "co2_energy")


def test_regional_climate_risk_types(regional_climate_risk_df):
    _typecheck(regional_climate_risk_df, RegionalClimateRiskRecord, "regional_climate_risk")


def test_company_esg_types(company_esg_df):
    _typecheck(company_esg_df, CompanyESGRecord, "company_esg")


def test_year_column_is_integer_like(co2_energy_df):
    # Accept int64 or float64-with-no-fractional-part (common after a CSV round-trip)
    years = co2_energy_df["year"]
    assert pd.api.types.is_numeric_dtype(years)
    assert (years.dropna() % 1 == 0).all(), "year column contains non-integer values"

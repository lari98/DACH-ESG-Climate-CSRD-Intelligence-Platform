"""11. Null-value test — every column that the Pydantic schema marks as *required*
(no default, not Optional) must have zero nulls in the cleaned data. Columns marked
Optional (e.g. electricity_price_eur_mwh, which free live sources don't publish) are
allowed to be null - that's an intentional, documented gap, not a defect."""
from __future__ import annotations

from app.validation.schemas import CO2EnergyRecord, CompanyESGRecord, RegionalClimateRiskRecord


def _required_fields(model) -> list[str]:
    return [name for name, field in model.model_fields.items() if field.is_required()]


def _assert_no_nulls_in_required_columns(df, model, dataset_name):
    required = _required_fields(model)
    for col in required:
        if col not in df.columns:
            continue  # covered separately by the column-existence test
        n_null = df[col].isna().sum()
        assert n_null == 0, (
            f"{dataset_name}.{col} is a required field but has {n_null} null value(s) "
            f"out of {len(df)} rows"
        )


def test_co2_energy_required_columns_have_no_nulls(co2_energy_df):
    _assert_no_nulls_in_required_columns(co2_energy_df, CO2EnergyRecord, "co2_energy")


def test_regional_climate_risk_required_columns_have_no_nulls(regional_climate_risk_df):
    _assert_no_nulls_in_required_columns(
        regional_climate_risk_df, RegionalClimateRiskRecord, "regional_climate_risk"
    )


def test_company_esg_required_columns_have_no_nulls(company_esg_df):
    _assert_no_nulls_in_required_columns(company_esg_df, CompanyESGRecord, "company_esg")


def test_optional_column_nullability_is_reported_not_failed(co2_energy_df, capsys):
    """Informational only: prints the null rate of optional columns (e.g. electricity
    price under live mode) so gaps are visible without breaking the test suite."""
    optional_cols = [
        name for name, field in CO2EnergyRecord.model_fields.items() if not field.is_required()
    ]
    for col in optional_cols:
        if col in co2_energy_df.columns:
            rate = co2_energy_df[col].isna().mean()
            print(f"[info] co2_energy.{col} null rate: {rate:.0%}")

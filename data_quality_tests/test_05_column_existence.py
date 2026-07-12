"""5. Column existence test — every column our Pydantic schema (the contract for
what's allowed into the database) expects must actually exist in the cleaned CSVs
we're about to load. This is the test that would have caught the earlier bug where
live-sourced files were silently skipped by the cleaner (columns never even reached
the cleaned/ folder)."""
from __future__ import annotations

from app.validation.schemas import CO2EnergyRecord, CompanyESGRecord, RegionalClimateRiskRecord

EXPECTED_COLUMNS = {
    "co2_energy": set(CO2EnergyRecord.model_fields.keys()),
    "regional_climate_risk": set(RegionalClimateRiskRecord.model_fields.keys()),
    "company_esg": set(CompanyESGRecord.model_fields.keys()),
}


def test_co2_energy_has_all_schema_columns(co2_energy_df):
    missing = EXPECTED_COLUMNS["co2_energy"] - set(co2_energy_df.columns)
    assert not missing, f"co2_energy.csv is missing columns required by CO2EnergyRecord: {missing}"


def test_regional_climate_risk_has_all_schema_columns(regional_climate_risk_df):
    missing = EXPECTED_COLUMNS["regional_climate_risk"] - set(regional_climate_risk_df.columns)
    assert not missing, f"regional_climate_risk.csv is missing columns required by RegionalClimateRiskRecord: {missing}"


def test_company_esg_has_all_schema_columns(company_esg_df):
    missing = EXPECTED_COLUMNS["company_esg"] - set(company_esg_df.columns)
    assert not missing, f"company_esg.csv is missing columns required by CompanyESGRecord: {missing}"

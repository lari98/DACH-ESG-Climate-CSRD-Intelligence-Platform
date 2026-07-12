"""9. Source completeness test — all 3 DACH countries must be represented in every
dataset; no country should silently drop out (e.g. because of an ISO alpha-2/alpha-3
mapping bug in the OWID merge)."""
from __future__ import annotations

from conftest import DACH_COUNTRIES


def test_co2_energy_has_all_dach_countries(co2_energy_df):
    present = set(co2_energy_df["country_code"].unique())
    missing = DACH_COUNTRIES - present
    assert not missing, f"co2_energy is missing countries: {missing}"


def test_regional_climate_risk_has_all_dach_countries(regional_climate_risk_df):
    present = set(regional_climate_risk_df["country_code"].unique())
    missing = DACH_COUNTRIES - present
    assert not missing, f"regional_climate_risk is missing countries: {missing}"


def test_company_esg_has_all_dach_countries(company_esg_df):
    present = set(company_esg_df["country_code"].unique())
    missing = DACH_COUNTRIES - present
    assert not missing, f"company_esg is missing countries: {missing}"


def test_no_dataset_is_completely_empty(all_dataframes):
    for name, df in all_dataframes.items():
        assert len(df) > 0, f"{name} is completely empty"

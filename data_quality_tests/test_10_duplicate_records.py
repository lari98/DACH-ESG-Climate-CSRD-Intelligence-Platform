"""10. Duplicate-record test — each dataset's natural key must be unique. Duplicates
here would mean double-counted emissions/risk/company rows downstream in every KPI,
chart, and AI answer that aggregates this data."""
from __future__ import annotations


def test_co2_energy_no_duplicate_country_year(co2_energy_df):
    dupes = co2_energy_df[co2_energy_df.duplicated(subset=["country_code", "year"], keep=False)]
    assert dupes.empty, f"Duplicate (country_code, year) rows in co2_energy:\n{dupes}"


def test_regional_climate_risk_no_duplicate_country_region(regional_climate_risk_df):
    dupes = regional_climate_risk_df[
        regional_climate_risk_df.duplicated(subset=["country_code", "region"], keep=False)
    ]
    assert dupes.empty, f"Duplicate (country_code, region) rows in regional_climate_risk:\n{dupes}"


def test_company_esg_no_duplicate_company_id(company_esg_df):
    dupes = company_esg_df[company_esg_df.duplicated(subset=["company_id"], keep=False)]
    assert dupes.empty, f"Duplicate company_id rows in company_esg:\n{dupes}"


def test_no_fully_duplicate_rows(all_dataframes):
    for name, df in all_dataframes.items():
        dupes = df[df.duplicated(keep=False)]
        assert dupes.empty, f"{name} contains {len(dupes)} fully-duplicate row(s)"

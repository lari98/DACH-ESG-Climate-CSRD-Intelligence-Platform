"""14. Referential-integrity test — country_code acts as the implicit foreign key
tying all three datasets together (the R dashboard and API join/filter on it across
tabs). Every value used anywhere must belong to the canonical DACH set, and every
dataset's country coverage must be mutually consistent."""
from __future__ import annotations

from conftest import DACH_COUNTRIES


def test_co2_energy_country_codes_are_valid(co2_energy_df):
    invalid = set(co2_energy_df["country_code"].unique()) - DACH_COUNTRIES
    assert not invalid, f"co2_energy has country_code values outside {DACH_COUNTRIES}: {invalid}"


def test_regional_climate_risk_country_codes_are_valid(regional_climate_risk_df):
    invalid = set(regional_climate_risk_df["country_code"].unique()) - DACH_COUNTRIES
    assert not invalid, f"regional_climate_risk has invalid country_code values: {invalid}"


def test_company_esg_country_codes_are_valid(company_esg_df):
    invalid = set(company_esg_df["country_code"].unique()) - DACH_COUNTRIES
    assert not invalid, f"company_esg has invalid country_code values: {invalid}"


def test_company_esg_countries_are_subset_of_co2_energy_countries(co2_energy_df, company_esg_df):
    """Every country a company is tagged with should also have macro co2/energy data,
    since the R dashboard cross-filters company rows against country-level charts."""
    co2_countries = set(co2_energy_df["country_code"].unique())
    company_countries = set(company_esg_df["country_code"].unique())
    orphans = company_countries - co2_countries
    assert not orphans, (
        f"company_esg references countries with no matching co2_energy rows: {orphans}"
    )


def test_regional_climate_risk_regions_are_non_empty_and_unique_per_country(regional_climate_risk_df):
    blank = regional_climate_risk_df[regional_climate_risk_df["region"].astype(str).str.strip() == ""]
    assert blank.empty, f"regional_climate_risk has {len(blank)} row(s) with a blank region name"

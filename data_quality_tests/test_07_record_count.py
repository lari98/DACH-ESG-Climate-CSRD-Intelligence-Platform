"""7. Record-count test — sanity bounds on row counts. Catches both "the source
returned nothing" (0 rows) and "something duplicated wildly" (absurdly high count)."""
from __future__ import annotations

# 3 DACH countries x plausible year range (OWID typically starts ~1850 for CO2, but our
# ingestion doesn't filter years - so just guard against 0 and against an implausibly
# huge number that would suggest a bad join/duplication bug).
BOUNDS = {
    "co2_energy": (3, 3 * 300),          # >=1 row/country, generously <=300 years/country
    "regional_climate_risk": (3, 500),   # a handful of regions per country
    "company_esg": (1, 100_000),         # demo company universe, generous upper bound
}


def test_co2_energy_record_count(co2_energy_df):
    lo, hi = BOUNDS["co2_energy"]
    assert lo <= len(co2_energy_df) <= hi, (
        f"co2_energy has {len(co2_energy_df)} rows, expected between {lo} and {hi}"
    )


def test_regional_climate_risk_record_count(regional_climate_risk_df):
    lo, hi = BOUNDS["regional_climate_risk"]
    assert lo <= len(regional_climate_risk_df) <= hi, (
        f"regional_climate_risk has {len(regional_climate_risk_df)} rows, expected between {lo} and {hi}"
    )


def test_company_esg_record_count(company_esg_df):
    lo, hi = BOUNDS["company_esg"]
    assert lo <= len(company_esg_df) <= hi, (
        f"company_esg has {len(company_esg_df)} rows, expected between {lo} and {hi}"
    )

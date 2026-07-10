import pandas as pd

from app.validation.checks import validate_dataframe
from app.validation.schemas import CO2EnergyRecord


def test_validate_dataframe_flags_bad_rows():
    df = pd.DataFrame([
        {"country_code": "DE", "year": 2020, "co2_emissions_mt": 700, "co2_per_capita_t": 8.4,
         "renewable_share_pct": 50, "fossil_share_pct": 40, "nuclear_share_pct": 10,
         "electricity_generation_twh": 500, "electricity_price_eur_mwh": 45, "data_quality": "sample"},
        {"country_code": "XX", "year": 2020, "co2_emissions_mt": 700, "co2_per_capita_t": 8.4,
         "renewable_share_pct": 50, "fossil_share_pct": 40, "nuclear_share_pct": 10,
         "electricity_generation_twh": 500, "electricity_price_eur_mwh": 45, "data_quality": "sample"},
    ])
    valid, report = validate_dataframe(df, CO2EnergyRecord, "co2_energy")
    assert report.total_rows == 2
    assert report.valid_rows == 1
    assert report.invalid_rows == 1
    assert not report.passed  # 50% < 95% gate

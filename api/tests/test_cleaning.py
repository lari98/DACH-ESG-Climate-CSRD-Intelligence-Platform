import pandas as pd

from app.cleaning.clean import clean_co2_energy, clean_regional_climate_risk


def test_clean_co2_energy_clips_and_dedupes():
    df = pd.DataFrame([
        {"country_code": "de", "year": 2020, "co2_emissions_mt": 700, "co2_per_capita_t": 8.4,
         "renewable_share_pct": 130, "fossil_share_pct": 40, "nuclear_share_pct": 10,
         "electricity_generation_twh": 500, "electricity_price_eur_mwh": 45, "data_quality": "sample"},
        {"country_code": "DE", "year": 2020, "co2_emissions_mt": 690, "co2_per_capita_t": 8.2,
         "renewable_share_pct": 50, "fossil_share_pct": 40, "nuclear_share_pct": 10,
         "electricity_generation_twh": 505, "electricity_price_eur_mwh": 46, "data_quality": "sample"},
    ])
    out = clean_co2_energy(df)
    assert len(out) == 1  # deduped on (country_code, year)
    assert out.iloc[0]["renewable_share_pct"] <= 100
    assert out.iloc[0]["country_code"] == "DE"


def test_clean_regional_climate_risk_clips_scores():
    df = pd.DataFrame([
        {"country_code": "at", "region": " Vienna ", "physical_risk_score": 12,
         "transition_risk_score": -1, "flood_risk_score": 5, "heat_stress_score": 5,
         "composite_climate_risk_score": 6, "risk_level": "Medium", "data_quality": "sample"},
    ])
    out = clean_regional_climate_risk(df)
    assert out.iloc[0]["physical_risk_score"] == 10
    assert out.iloc[0]["transition_risk_score"] == 0
    assert out.iloc[0]["region"] == "Vienna"

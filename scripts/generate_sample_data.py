"""
generate_sample_data.py
========================
Generates the offline / local-dev SAMPLE dataset for the DACH ESG, Climate Risk &
CSRD Intelligence Platform.

IMPORTANT — DATA PROVENANCE:
This sandbox environment has no outbound network access to the real public data
providers (Our World in Data, Eurostat, DESTATIS, Statistik Austria, BFS). The
production ingestion pipeline (see `python/app/ingestion/`) is built to pull from
those live sources. To keep the project runnable end-to-end without network access,
this script generates a clearly-labeled SAMPLE dataset with realistic trend shapes
and orders of magnitude (grounded in well-known public figures, e.g. Germany's
annual CO2 emissions being on the order of ~650-750 Mt and falling, Austria's
renewable electricity share being roughly 75-80%+, Switzerland's electricity mix
being hydro/nuclear dominated with very low grid carbon intensity).

Every row is tagged `data_quality = "sample"` and every output file is written under
`data/sample/` (never under `data/raw` or `data/cleaned`, which are reserved for real
ingested data) so the dashboard and reports can clearly flag demo vs. real data,
per the project's "no fake static visuals, always label sample data" requirement.

Run:
    python scripts/generate_sample_data.py
"""
from __future__ import annotations

import math
import random
from pathlib import Path

import pandas as pd

random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "sample"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COUNTRIES = {
    "DE": {"name": "Germany", "name_de": "Deutschland", "co2_base": 940, "co2_2023": 673,
           "renew_base": 6, "renew_2023": 52, "pop_m": 84.7},
    "AT": {"name": "Austria", "name_de": "Österreich", "co2_base": 62, "co2_2023": 57,
           "renew_base": 60, "renew_2023": 78, "pop_m": 9.1},
    "CH": {"name": "Switzerland", "name_de": "Schweiz", "co2_base": 41, "co2_2023": 33,
           "renew_base": 68, "renew_2023": 79, "pop_m": 8.8},
}

YEARS = list(range(2000, 2024))

REGIONS = {
    "DE": ["Bavaria", "North Rhine-Westphalia", "Baden-Württemberg", "Lower Saxony",
           "Hesse", "Saxony", "Berlin", "Brandenburg"],
    "AT": ["Vienna", "Lower Austria", "Upper Austria", "Styria", "Tyrol",
           "Carinthia", "Salzburg", "Vorarlberg"],
    "CH": ["Zurich", "Bern", "Vaud", "Geneva", "Aargau", "St. Gallen", "Ticino", "Valais"],
}


def smooth_series(start: float, end: float, n: int, noise: float = 0.015) -> list[float]:
    vals = []
    for i in range(n):
        t = i / (n - 1)
        # ease-out curve so recent years move faster (policy acceleration)
        eased = 1 - (1 - t) ** 1.6
        base = start + (end - start) * eased
        vals.append(round(base * (1 + random.uniform(-noise, noise)), 2))
    return vals


def build_co2_energy() -> pd.DataFrame:
    rows = []
    for code, meta in COUNTRIES.items():
        co2_series = smooth_series(meta["co2_base"], meta["co2_2023"], len(YEARS))
        renew_series = smooth_series(meta["renew_base"], meta["renew_2023"], len(YEARS))
        for yr, co2, renew in zip(YEARS, co2_series, renew_series):
            fossil = max(0, 100 - renew - random.uniform(3, 8))
            nuclear = max(0, 100 - renew - fossil)
            electricity_twh = round(meta["pop_m"] * random.uniform(6.0, 7.5), 1)
            price_eur_mwh = round(35 + (yr - 2000) * 2.1 + random.uniform(-8, 15), 2)
            rows.append({
                "country_code": code,
                "country_name": meta["name"],
                "country_name_de": meta["name_de"],
                "year": yr,
                "co2_emissions_mt": co2,
                "co2_per_capita_t": round(co2 * 1_000_000 / (meta["pop_m"] * 1_000_000), 2),
                "renewable_share_pct": renew,
                "fossil_share_pct": round(fossil, 1),
                "nuclear_share_pct": round(nuclear, 1),
                "electricity_generation_twh": electricity_twh,
                "electricity_price_eur_mwh": price_eur_mwh,
                "data_quality": "sample",
            })
    return pd.DataFrame(rows)


def build_regional_climate_risk() -> pd.DataFrame:
    rows = []
    for code, regions in REGIONS.items():
        for region in regions:
            physical_risk = round(random.uniform(1.5, 8.5), 1)
            transition_risk = round(random.uniform(1.5, 8.5), 1)
            flood_risk = round(random.uniform(0, 10), 1)
            heat_risk = round(random.uniform(0, 10), 1)
            composite = round((physical_risk + transition_risk) / 2, 1)
            rows.append({
                "country_code": code,
                "region": region,
                "physical_risk_score": physical_risk,
                "transition_risk_score": transition_risk,
                "flood_risk_score": flood_risk,
                "heat_stress_score": heat_risk,
                "composite_climate_risk_score": composite,
                "risk_level": ("Low" if composite < 4 else "Medium" if composite < 7 else "High"),
                "data_quality": "sample",
            })
    return pd.DataFrame(rows)


def build_esg_company_sample() -> pd.DataFrame:
    sectors = ["Energy", "Financial Services", "Manufacturing", "Industrials",
               "Consumer Goods", "Technology", "Real Estate", "Transportation"]
    rows = []
    for i in range(1, 41):
        code = random.choice(list(COUNTRIES.keys()))
        sector = random.choice(sectors)
        scope1 = round(random.uniform(500, 250000), 1)
        scope2 = round(random.uniform(200, 120000), 1)
        scope3 = round(random.uniform(2000, 900000), 1)
        esg_readiness = round(random.uniform(20, 95), 1)
        csrd_readiness = round(random.uniform(15, 90), 1)
        rows.append({
            "company_id": f"SAMPLE-{i:03d}",
            "company_name": f"Sample Company {i}",
            "country_code": code,
            "sector": sector,
            "scope1_tco2e": scope1,
            "scope2_tco2e": scope2,
            "scope3_tco2e": scope3,
            "esg_readiness_score": esg_readiness,
            "csrd_readiness_score": csrd_readiness,
            "reporting_gaps_count": random.randint(0, 12),
            "data_quality": "sample",
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    co2_energy = build_co2_energy()
    climate_risk = build_regional_climate_risk()
    esg_companies = build_esg_company_sample()

    co2_energy.to_csv(OUT_DIR / "sample_co2_energy_dach.csv", index=False)
    climate_risk.to_csv(OUT_DIR / "sample_regional_climate_risk.csv", index=False)
    esg_companies.to_csv(OUT_DIR / "sample_company_esg.csv", index=False)

    print(f"Wrote {len(co2_energy)} rows -> sample_co2_energy_dach.csv")
    print(f"Wrote {len(climate_risk)} rows -> sample_regional_climate_risk.csv")
    print(f"Wrote {len(esg_companies)} rows -> sample_company_esg.csv")

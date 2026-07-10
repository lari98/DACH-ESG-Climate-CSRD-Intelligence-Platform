"""Cleaning / standardization layer — raw CSVs -> conformed cleaned CSVs.

Equivalent in spirit to the Databricks Silver layer, but runnable locally with
pandas so the whole pipeline works without a Spark cluster.
"""
from __future__ import annotations

import pandas as pd

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

REQUIRED_CO2_ENERGY_COLUMNS = [
    "country_code", "year", "co2_emissions_mt", "renewable_share_pct",
]


def clean_co2_energy(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize types, drop duplicates, clip out-of-range percentages."""
    df = df.copy()
    df["country_code"] = df["country_code"].str.upper().str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    numeric_cols = [
        "co2_emissions_mt", "co2_per_capita_t", "renewable_share_pct",
        "fossil_share_pct", "nuclear_share_pct", "electricity_generation_twh",
        "electricity_price_eur_mwh",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for pct_col in ["renewable_share_pct", "fossil_share_pct", "nuclear_share_pct"]:
        if pct_col in df.columns:
            df[pct_col] = df[pct_col].clip(lower=0, upper=100)

    df = df.dropna(subset=REQUIRED_CO2_ENERGY_COLUMNS)
    df = df.drop_duplicates(subset=["country_code", "year"], keep="last")
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)
    logger.info("Cleaned co2_energy: %d rows remain", len(df))
    return df


def clean_regional_climate_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["country_code"] = df["country_code"].str.upper().str.strip()
    df["region"] = df["region"].str.strip()
    score_cols = [c for c in df.columns if c.endswith("_score")]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").clip(lower=0, upper=10)
    df = df.dropna(subset=["country_code", "region"])
    df = df.drop_duplicates(subset=["country_code", "region"], keep="last")
    logger.info("Cleaned regional_climate_risk: %d rows remain", len(df))
    return df


def clean_company_esg(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["country_code"] = df["country_code"].str.upper().str.strip()
    for col in ["scope1_tco2e", "scope2_tco2e", "scope3_tco2e",
                "esg_readiness_score", "csrd_readiness_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").clip(lower=0)
    df = df.dropna(subset=["company_id", "country_code"])
    df = df.drop_duplicates(subset=["company_id"], keep="last")
    logger.info("Cleaned company_esg: %d rows remain", len(df))
    return df


CLEANERS = {
    "co2_energy": clean_co2_energy,
    "regional_climate_risk": clean_regional_climate_risk,
    "company_esg": clean_company_esg,
}


def run() -> list[str]:
    """Reads every raw CSV, infers which cleaner to use by filename, writes to data/cleaned."""
    settings = get_settings()
    settings.cleaned_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for raw_file in settings.raw_dir.glob("*.csv"):
        key = next((k for k in CLEANERS if k.replace("_", "") in raw_file.stem.replace("_", "")), None)
        if key is None:
            logger.warning("No cleaner matched for %s, skipping", raw_file.name)
            continue
        df = pd.read_csv(raw_file)
        cleaned = CLEANERS[key](df)
        out_path = settings.cleaned_dir / f"{key}.csv"
        cleaned.to_csv(out_path, index=False)
        written.append(str(out_path))
    return written


if __name__ == "__main__":
    files = run()
    print(f"Cleaned {len(files)} file(s):")
    for f in files:
        print(f"  - {f}")

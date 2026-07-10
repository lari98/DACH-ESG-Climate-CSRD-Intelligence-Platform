"""
Live data source connectors.

These hit real public endpoints (Our World in Data on GitHub, Eurostat REST API).
They are used when `settings.data_mode == "live"`. Each function returns a raw
pandas DataFrame exactly as received (no cleaning) — cleaning happens in
`app/cleaning`. If a live fetch fails (e.g. no network), the caller falls back to
the bundled sample dataset so the pipeline never hard-crashes.
"""
from __future__ import annotations

import pandas as pd
import requests

from app.core.logging import get_logger

logger = get_logger(__name__)

OWID_CO2_URL = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
OWID_ENERGY_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
EUROSTAT_API_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

DACH_COUNTRIES = ["DEU", "AUT", "CHE"]  # ISO-3166 alpha-3, used by OWID


def fetch_owid_co2(timeout: int = 20) -> pd.DataFrame:
    """Fetch the full OWID CO2 dataset and filter to DE/AT/CH."""
    logger.info("Fetching OWID CO2 dataset from %s", OWID_CO2_URL)
    resp = requests.get(OWID_CO2_URL, timeout=timeout)
    resp.raise_for_status()
    from io import StringIO

    df = pd.read_csv(StringIO(resp.text))
    return df[df["iso_code"].isin(DACH_COUNTRIES)].copy()


def fetch_owid_energy(timeout: int = 20) -> pd.DataFrame:
    """Fetch the full OWID energy-mix dataset and filter to DE/AT/CH."""
    logger.info("Fetching OWID energy dataset from %s", OWID_ENERGY_URL)
    resp = requests.get(OWID_ENERGY_URL, timeout=timeout)
    resp.raise_for_status()
    from io import StringIO

    df = pd.read_csv(StringIO(resp.text))
    return df[df["iso_code"].isin(DACH_COUNTRIES)].copy()


ISO3_TO_ISO2 = {"DEU": "DE", "AUT": "AT", "CHE": "CH"}

# OWID source column -> our schema column. Only columns present in the live CSV are used;
# missing ones (e.g. electricity price, which OWID doesn't publish) are left NaN rather
# than dropping the whole row, since only country_code/year/co2_emissions_mt/
# renewable_share_pct are actually required downstream (see clean.REQUIRED_CO2_ENERGY_COLUMNS).
_CO2_COL_MAP = {"co2": "co2_emissions_mt", "co2_per_capita": "co2_per_capita_t"}
_ENERGY_COL_MAP = {
    "renewables_share_energy": "renewable_share_pct",
    "fossil_share_energy": "fossil_share_pct",
    "nuclear_share_energy": "nuclear_share_pct",
    "electricity_generation": "electricity_generation_twh",
}


def fetch_and_merge_co2_energy(timeout: int = 20) -> pd.DataFrame:
    """Fetch OWID CO2 + energy datasets and conform them to our co2_energy schema in one
    step, so the output can be written straight into data/raw and picked up correctly by
    the cleaning layer (same column names/types as the sample dataset, tagged 'official').
    """
    co2_raw = fetch_owid_co2(timeout=timeout)
    energy_raw = fetch_owid_energy(timeout=timeout)

    co2_cols = {k: v for k, v in _CO2_COL_MAP.items() if k in co2_raw.columns}
    energy_cols = {k: v for k, v in _ENERGY_COL_MAP.items() if k in energy_raw.columns}

    co2 = co2_raw[["iso_code", "year", *co2_cols.keys()]].rename(columns=co2_cols)
    energy = energy_raw[["iso_code", "year", *energy_cols.keys()]].rename(columns=energy_cols)

    merged = pd.merge(co2, energy, on=["iso_code", "year"], how="inner")
    merged["country_code"] = merged["iso_code"].map(ISO3_TO_ISO2)
    merged = merged.drop(columns=["iso_code"]).dropna(subset=["country_code"])

    if "electricity_price_eur_mwh" not in merged.columns:
        # Not published by any free API we've wired up yet — honestly left blank rather
        # than faked, see docs/04_data_freshness_and_accuracy.md.
        merged["electricity_price_eur_mwh"] = pd.NA

    merged["data_quality"] = "official"
    return merged


def fetch_eurostat_dataset(dataset_code: str, params: dict | None = None, timeout: int = 20) -> dict:
    """Fetch a raw JSON-stat dataset from Eurostat's REST API (e.g. 'env_air_gge')."""
    url = f"{EUROSTAT_API_BASE}/{dataset_code}"
    logger.info("Fetching Eurostat dataset %s", dataset_code)
    resp = requests.get(url, params=params or {}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

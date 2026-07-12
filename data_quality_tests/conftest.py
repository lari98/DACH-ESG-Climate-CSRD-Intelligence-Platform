"""Shared fixtures for the data-quality / source test suite.

This folder is intentionally separate from api/tests/ (which tests application code
- endpoints, cleaning functions, AI grounding, etc). data_quality_tests/ instead tests
the *data itself*: are the free source APIs reachable, does the schema match, is the
data complete/fresh/duplicate-free/PII-free, etc. Run with:

    cd data_quality_tests
    pytest -v

or from the project root: pytest data_quality_tests -v

Tests that need real network access (source availability/connection/schema tests)
skip cleanly (not fail) when offline, since this suite should also be runnable in
CI or air-gapped environments without turning "no internet" into a false failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "api"))

from app.core.config import get_settings  # noqa: E402
from app.ingestion import sources  # noqa: E402

settings = get_settings()

DATASETS = ["co2_energy", "regional_climate_risk", "company_esg"]
DACH_COUNTRIES = {"DE", "AT", "CH"}


def _load_cleaned(name: str) -> pd.DataFrame:
    path = settings.cleaned_dir / f"{name}.csv"
    if not path.exists():
        pytest.skip(
            f"data/cleaned/{name}.csv not found - run the ingestion pipeline first "
            f"(api/start_api.bat or: python -m app.ingestion.run_all && "
            f"python -m app.cleaning.clean)"
        )
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def co2_energy_df() -> pd.DataFrame:
    return _load_cleaned("co2_energy")


@pytest.fixture(scope="session")
def regional_climate_risk_df() -> pd.DataFrame:
    return _load_cleaned("regional_climate_risk")


@pytest.fixture(scope="session")
def company_esg_df() -> pd.DataFrame:
    return _load_cleaned("company_esg")


@pytest.fixture(scope="session")
def all_dataframes(co2_energy_df, regional_climate_risk_df, company_esg_df):
    return {
        "co2_energy": co2_energy_df,
        "regional_climate_risk": regional_climate_risk_df,
        "company_esg": company_esg_df,
    }


def has_network() -> bool:
    """Best-effort check so live-source tests skip instead of failing when offline."""
    try:
        import requests

        requests.head("https://raw.githubusercontent.com", timeout=5)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def network_available() -> bool:
    return has_network()

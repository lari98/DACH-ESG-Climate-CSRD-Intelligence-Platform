"""Lightweight runtime/performance smoke tests. Not a load-testing replacement
(see docs/08_testing_strategy.md for the recommended Locust/k6 follow-up), but
catches obvious regressions (e.g. an accidental O(n^2) loop) directly in CI."""
import time

import pandas as pd

from app.cleaning.clean import clean_co2_energy
from app.validation.checks import validate_dataframe
from app.validation.schemas import CO2EnergyRecord


def _make_large_df(n=5000):
    countries = ["DE", "AT", "CH"]
    rows = []
    for i in range(n):
        rows.append({
            "country_code": countries[i % 3], "year": 2000 + (i % 24),
            "co2_emissions_mt": 500 + i * 0.01, "co2_per_capita_t": 7.5,
            "renewable_share_pct": 40, "fossil_share_pct": 50, "nuclear_share_pct": 10,
            "electricity_generation_twh": 500, "electricity_price_eur_mwh": 60,
            "data_quality": "sample",
        })
    return pd.DataFrame(rows)


def test_cleaning_scales_reasonably():
    df = _make_large_df(5000)
    start = time.time()
    cleaned = clean_co2_energy(df)
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Cleaning 5000 rows took {elapsed:.2f}s, expected < 5s"
    assert len(cleaned) > 0


def test_validation_scales_reasonably():
    df = _make_large_df(2000)
    start = time.time()
    _, report = validate_dataframe(df, CO2EnergyRecord, "co2_energy")
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Validating 2000 rows took {elapsed:.2f}s, expected < 5s"
    assert report.total_rows == 2000


def test_api_health_endpoint_responds_quickly():
    import os
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    from fastapi.testclient import TestClient

    from app.api.main import app
    client = TestClient(app)
    start = time.time()
    resp = client.get("/health")
    elapsed = time.time() - start
    assert resp.status_code == 200
    assert elapsed < 1.0

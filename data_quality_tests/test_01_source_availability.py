"""1. Source availability test — are the free public source endpoints up at all?"""
from __future__ import annotations

import pytest
import requests

from app.ingestion.sources import EUROSTAT_API_BASE, OWID_CO2_URL, OWID_ENERGY_URL


@pytest.mark.parametrize("url", [OWID_CO2_URL, OWID_ENERGY_URL])
def test_owid_source_is_available(network_available, url):
    if not network_available:
        pytest.skip("No network access in this environment")
    resp = requests.head(url, timeout=10, allow_redirects=True)
    assert resp.status_code < 400, f"{url} returned {resp.status_code}"


def test_eurostat_base_is_available(network_available):
    if not network_available:
        pytest.skip("No network access in this environment")
    # Eurostat's base dissemination API rejects a bare HEAD with 404/405 depending on
    # routing, so just confirm the host itself resolves and responds to something.
    resp = requests.get(EUROSTAT_API_BASE.rsplit("/", 1)[0], timeout=10)
    assert resp.status_code < 500, f"Eurostat host errored with {resp.status_code}"

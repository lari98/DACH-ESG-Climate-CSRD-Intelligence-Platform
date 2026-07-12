"""3. Authentication test — confirms the "free, no hidden charges" claim: every wired
data source must work with zero API key / zero Authorization header, and the codebase
must not silently require a paid credential anywhere in the ingestion path."""
from __future__ import annotations

import inspect

import pytest
import requests

from app.ingestion import sources


@pytest.mark.parametrize("fetch_fn_name", ["fetch_owid_co2", "fetch_owid_energy"])
def test_owid_fetch_functions_send_no_auth_header(fetch_fn_name):
    """Static check: the fetch functions must never attach Authorization/API-key headers."""
    src = inspect.getsource(getattr(sources, fetch_fn_name))
    lowered = src.lower()
    for forbidden in ["authorization", "api_key", "apikey", "x-api-key", "bearer "]:
        assert forbidden not in lowered, (
            f"{fetch_fn_name} appears to reference '{forbidden}' - free sources should "
            f"need no credential at all"
        )


def test_owid_co2_works_with_no_auth_header(network_available):
    if not network_available:
        pytest.skip("No network access in this environment")
    resp = requests.head(sources.OWID_CO2_URL, timeout=10)  # deliberately no headers
    assert resp.status_code < 400, "OWID CO2 source unexpectedly requires authentication"


def test_no_azure_openai_key_required_for_core_data_pipeline():
    """AZURE_OPENAI_API_KEY must only gate the *optional* AI features, never the core
    ingest -> clean -> validate -> load data pipeline (documented in
    docs/04_data_freshness_and_accuracy.md and docs/09_deployment_guide.md)."""
    from app.ingestion import run_all
    from app.cleaning import clean
    from app.db import session as db_session

    for module in (run_all, clean, db_session):
        src = inspect.getsource(module)
        assert "AZURE_OPENAI" not in src, (
            f"{module.__name__} references AZURE_OPENAI - the core data pipeline must "
            f"stay usable with zero paid credentials"
        )

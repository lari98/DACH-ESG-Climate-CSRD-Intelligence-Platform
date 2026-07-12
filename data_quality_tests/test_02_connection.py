"""2. Connection test — can we actually open a connection and get a real response
(not just a HEAD ping), to each source, the local API, and the local database?"""
from __future__ import annotations

import pytest
import requests
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine


def test_owid_co2_connection(network_available):
    if not network_available:
        pytest.skip("No network access in this environment")
    from app.ingestion.sources import OWID_CO2_URL

    resp = requests.get(OWID_CO2_URL, timeout=15, stream=True)
    assert resp.status_code == 200
    # Read a small chunk to confirm the connection actually streams data, not just headers.
    chunk = next(resp.iter_content(chunk_size=1024), b"")
    assert len(chunk) > 0
    resp.close()


def test_local_api_connection():
    """Optional: only runs if the FastAPI service happens to be up on localhost:8000."""
    base = "http://localhost:8000"
    try:
        resp = requests.get(f"{base}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        pytest.skip("Local API not running on :8000 - start it with api/start_api.bat to include this check")
        return
    assert resp.status_code == 200


def test_database_connection():
    settings = get_settings()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"Could not connect to database at {settings.database_url}: {exc}")

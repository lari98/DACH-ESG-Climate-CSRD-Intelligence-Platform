"""4. Source schema test — the RAW live source columns we depend on for the
OWID -> our-schema merge (app.ingestion.sources.fetch_and_merge_co2_energy) must
still exist. This is the test that would have caught the "OWID renamed a column"
class of breakage before it silently produced empty/garbage merged rows."""
from __future__ import annotations

import pytest

from app.ingestion.sources import (
    _CO2_COL_MAP,
    _ENERGY_COL_MAP,
    fetch_owid_co2,
    fetch_owid_energy,
)

# Minimum column sets our merge logic needs. iso_code/year are the join keys;
# co2 and renewables_share_energy are the two headline metrics the whole
# "live" mode exists to provide - if either disappears, live mode degrades
# to a near-empty dataset silently, which is exactly the class of bug we want
# a schema test to catch before it reaches production.
REQUIRED_CO2_RAW_COLUMNS = {"iso_code", "year", "co2"}
REQUIRED_ENERGY_RAW_COLUMNS = {"iso_code", "year", "renewables_share_energy"}


def test_owid_co2_raw_schema_has_required_columns(network_available):
    if not network_available:
        pytest.skip("No network access in this environment")
    df = fetch_owid_co2()
    missing = REQUIRED_CO2_RAW_COLUMNS - set(df.columns)
    assert not missing, f"OWID CO2 source is missing expected columns: {missing}"


def test_owid_energy_raw_schema_has_required_columns(network_available):
    if not network_available:
        pytest.skip("No network access in this environment")
    df = fetch_owid_energy()
    missing = REQUIRED_ENERGY_RAW_COLUMNS - set(df.columns)
    assert not missing, f"OWID energy source is missing expected columns: {missing}"


def test_column_maps_cover_the_required_columns():
    """The rename maps in sources.py must at least attempt every required column,
    independent of network access - a pure code-consistency check."""
    assert "co2" in _CO2_COL_MAP
    assert "renewables_share_energy" in _ENERGY_COL_MAP

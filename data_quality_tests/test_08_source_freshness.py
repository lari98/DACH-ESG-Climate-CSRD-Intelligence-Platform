"""8. Source freshness test — is the newest data point recent enough to be useful?

Honest framing (see docs/04_data_freshness_and_accuracy.md): OWID CO2/energy data is
official annual statistics with a real-world publication lag of roughly 1-2 years, not
true real-time. This test checks for *staleness beyond that expected lag*, not for
literal same-day freshness - a dataset stuck 10 years in the past would fail this;
a dataset 1-2 years behind today is normal and expected."""
from __future__ import annotations

from datetime import datetime, timezone

MAX_EXPECTED_LAG_YEARS = 5  # generous ceiling; OWID's real lag is usually 1-2 years


def test_co2_energy_not_stale(co2_energy_df):
    current_year = datetime.now(timezone.utc).year
    newest_year = int(co2_energy_df["year"].max())
    lag = current_year - newest_year
    assert lag <= MAX_EXPECTED_LAG_YEARS, (
        f"Newest co2_energy data point is from {newest_year}, {lag} years behind "
        f"{current_year} - exceeds the expected publication lag, dataset may be stuck/stale"
    )


def test_raw_ingestion_files_have_valid_recent_timestamp():
    """Every live-pulled raw filename is stamped app.ingestion.run_all._stamp() at fetch
    time - confirm any live-tagged raw files present are recent, not leftover debris."""
    import re
    from datetime import datetime as dt

    from app.core.config import get_settings

    settings = get_settings()
    if not settings.raw_dir.exists():
        return  # nothing ingested yet - not a freshness failure, just no data
    pattern = re.compile(r"_(\d{8}T\d{6}Z)\.csv$")
    now = dt.now(timezone.utc)
    for f in settings.raw_dir.glob("owid_*.csv"):
        m = pattern.search(f.name)
        assert m, f"{f.name} doesn't match the expected timestamp naming convention"
        stamp = dt.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        age_days = (now - stamp).days
        assert age_days < 365, f"{f.name} is {age_days} days old - looks like stale leftover debris"

"""13. Timestamp-format test — every time-like value in the pipeline must parse
cleanly: the `year` column as a sane 4-digit year, and the ingestion-run timestamp
embedded in live raw filenames as valid ISO-8601-ish UTC (app.ingestion.run_all._stamp,
format %Y%m%dT%H%M%SZ)."""
from __future__ import annotations

import re
from datetime import datetime

YEAR_PATTERN_MIN, YEAR_PATTERN_MAX = 1990, 2100
STAMP_RE = re.compile(r"^\d{8}T\d{6}Z$")


def test_year_values_are_in_sane_range(co2_energy_df):
    bad = co2_energy_df[
        (co2_energy_df["year"] < YEAR_PATTERN_MIN) | (co2_energy_df["year"] > YEAR_PATTERN_MAX)
    ]
    assert bad.empty, f"co2_energy has out-of-range year values:\n{bad[['country_code', 'year']]}"


def test_raw_filename_timestamps_parse_as_valid_utc():
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.raw_dir.exists():
        return
    for f in settings.raw_dir.glob("owid_*.csv"):
        m = re.search(r"_(\d{8}T\d{6}Z)\.csv$", f.name)
        assert m, f"{f.name} does not contain a timestamp in the expected _%Y%m%dT%H%M%SZ.csv format"
        stamp_str = m.group(1)
        assert STAMP_RE.match(stamp_str), f"{stamp_str} (from {f.name}) doesn't match the stamp pattern"
        # Must actually parse as a real datetime, not just match the regex shape.
        parsed = datetime.strptime(stamp_str, "%Y%m%dT%H%M%SZ")
        assert parsed.year >= 2020, f"{f.name} timestamp parsed to an implausible year {parsed.year}"

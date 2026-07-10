import pandas as pd

from app.validation.reconciliation import reconcile


def test_reconcile_flags_large_jump():
    previous = pd.DataFrame([
        {"country_code": "DE", "year": 2023, "co2_emissions_mt": 670, "renewable_share_pct": 52},
    ])
    new = pd.DataFrame([
        {"country_code": "DE", "year": 2023, "co2_emissions_mt": 10, "renewable_share_pct": 52},  # bad pull
    ])
    safe, report = reconcile("co2_energy", new, previous)
    assert not report.clean
    assert report.anomaly_count == 1
    assert len(safe) == 0  # anomalous row withheld


def test_reconcile_passes_small_change():
    previous = pd.DataFrame([
        {"country_code": "DE", "year": 2023, "co2_emissions_mt": 670, "renewable_share_pct": 52},
    ])
    new = pd.DataFrame([
        {"country_code": "DE", "year": 2023, "co2_emissions_mt": 665, "renewable_share_pct": 53},
    ])
    safe, report = reconcile("co2_energy", new, previous)
    assert report.clean
    assert len(safe) == 1


def test_reconcile_no_previous_promotes_all():
    new = pd.DataFrame([
        {"country_code": "DE", "year": 2023, "co2_emissions_mt": 665, "renewable_share_pct": 53},
    ])
    safe, report = reconcile("co2_energy", new, None)
    assert len(safe) == 1
    assert report.rows_compared == 0

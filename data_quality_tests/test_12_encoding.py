"""12. Encoding test — text columns (company names, sectors, region names, which
legitimately contain German characters like ä/ö/ü/ß) must be clean valid UTF-8, with
no mojibake or Unicode replacement characters from a broken decode step."""
from __future__ import annotations

REPLACEMENT_CHAR = "�"

TEXT_COLUMNS = {
    "co2_energy": ["country_code", "data_quality"],
    "regional_climate_risk": ["country_code", "region", "risk_level", "data_quality"],
    "company_esg": ["company_id", "company_name", "country_code", "sector", "data_quality"],
}


def _assert_clean_utf8(df, columns, dataset_name):
    for col in columns:
        if col not in df.columns:
            continue
        for value in df[col].dropna().astype(str):
            assert REPLACEMENT_CHAR not in value, (
                f"{dataset_name}.{col} contains a Unicode replacement character "
                f"(U+FFFD) in value {value!r} - likely a broken encoding/decoding step"
            )
            # Round-trip through UTF-8 must be lossless.
            assert value.encode("utf-8").decode("utf-8") == value, (
                f"{dataset_name}.{col} value {value!r} is not valid round-trippable UTF-8"
            )


def test_co2_energy_text_columns_are_valid_utf8(co2_energy_df):
    _assert_clean_utf8(co2_energy_df, TEXT_COLUMNS["co2_energy"], "co2_energy")


def test_regional_climate_risk_text_columns_are_valid_utf8(regional_climate_risk_df):
    _assert_clean_utf8(
        regional_climate_risk_df, TEXT_COLUMNS["regional_climate_risk"], "regional_climate_risk"
    )


def test_company_esg_text_columns_are_valid_utf8(company_esg_df):
    _assert_clean_utf8(company_esg_df, TEXT_COLUMNS["company_esg"], "company_esg")


def test_cleaned_csv_files_are_utf8_on_disk():
    """Confirm the files themselves were written as UTF-8 (not e.g. Windows cp1252,
    which would corrupt German umlauts silently on some systems)."""
    from app.core.config import get_settings

    settings = get_settings()
    for name in ["co2_energy", "regional_climate_risk", "company_esg"]:
        path = settings.cleaned_dir / f"{name}.csv"
        if not path.exists():
            continue
        with open(path, "rb") as f:
            raw = f.read()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AssertionError(f"{path} is not valid UTF-8 on disk: {exc}") from exc

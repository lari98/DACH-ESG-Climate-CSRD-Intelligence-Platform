# Data Quality Test Suite

Separate from `api/tests/` (which tests application *code* — endpoints, cleaning
functions, AI grounding). This folder tests the **data itself**: is the free source
reachable, does its schema match what we expect, is what lands in the database
complete, duplicate-free, correctly typed, free of PII, etc.

## Requirements

Uses the same dependencies as `api/` (pandas, pydantic, sqlalchemy, requests, pytest).
If you've already run `api/start_api.bat` once, they're installed. Otherwise:

```bash
cd api
pip install -r requirements.txt
```

## Running

You need cleaned data on disk first (most tests read `data/cleaned/*.csv`):

```bash
cd api
python -m app.ingestion.run_all
python -m app.cleaning.clean
```

Then, from the project root:

```bash
pytest data_quality_tests -v
```

or from inside the folder:

```bash
cd data_quality_tests
pytest
```

## What each file covers

| File | Test |
|---|---|
| `test_01_source_availability.py` | Are the free source endpoints (OWID, Eurostat) up at all? |
| `test_02_connection.py` | Can we open a real connection and read data (not just ping), incl. local API + DB |
| `test_03_authentication.py` | Confirms every source needs zero API key / Authorization header |
| `test_04_source_schema.py` | Do the raw OWID CSVs still have the columns our merge logic depends on? |
| `test_05_column_existence.py` | Does every column our Pydantic schema expects exist in the cleaned CSVs? |
| `test_06_data_type.py` | Does every value actually validate against its expected type? |
| `test_07_record_count.py` | Sanity bounds — not zero rows, not an absurd duplication blowup |
| `test_08_source_freshness.py` | Is the newest data point within the expected publication lag? |
| `test_09_source_completeness.py` | Are all 3 DACH countries present in every dataset? |
| `test_10_duplicate_records.py` | No duplicate natural keys (country+year, country+region, company_id) |
| `test_11_null_values.py` | Zero nulls in *required* schema fields; optional-field nulls are reported, not failed |
| `test_12_encoding.py` | Text columns (German umlauts etc.) are clean, lossless UTF-8 |
| `test_13_timestamp_format.py` | `year` values and ingestion-run timestamps parse correctly |
| `test_14_referential_integrity.py` | country_code values are valid and mutually consistent across datasets |
| `test_15_personal_data_classification.py` | No accidental personal data (emails, IBANs, PII-signature columns) |

## Notes on skipped tests

Tests that need real internet access (source availability/connection/schema) **skip**
cleanly rather than fail when offline, so this suite stays usable in restricted/CI
environments. On your own machine with normal internet access, none should skip.

## Honest scope

`regional_climate_risk` and `company_esg` remain synthetic/sample data even in
`DATA_MODE=live` — there is no free, no-key public API for company-level ESG scores
or regional climate-risk scores (see `docs/04_data_freshness_and_accuracy.md`). Only
`co2_energy` is genuinely live-sourced from Our World in Data. The freshness and
completeness tests are written to reflect this honestly rather than pretend otherwise.

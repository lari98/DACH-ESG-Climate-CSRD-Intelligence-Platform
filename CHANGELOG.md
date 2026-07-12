# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):
- **MAJOR** — breaking changes (e.g. API contract changes, folder restructures)
- **MINOR** — new features, additive and backward-compatible
- **PATCH** — bug fixes, no new features

Current version: **1.7.0** (see `VERSION`)

## [1.7.0] - Self-healing database schema

- Added an auto-migration engine (`app/db/session.py: ensure_schema_up_to_date`) that
  detects column drift (missing columns, nullable/NOT NULL mismatches) and repairs the
  SQLite schema in place, automatically, every time the API starts.
- Wired it into a FastAPI startup hook (`app/api/main.py`), so it also runs on every
  `uvicorn --reload` auto-restart — schema fixes now apply themselves with no manual
  migration step or terminal command required.

## [1.6.0] - Data quality test suite

- Added `data_quality_tests/`, a standalone pytest suite (separate from `api/tests/`)
  covering 15 categories: source availability, connection, authentication, source
  schema, column existence, data-type, record-count, source freshness, source
  completeness, duplicate-record, null-value, encoding, timestamp-format,
  referential-integrity, and personal-data classification.
- Added a `data-quality-tests` job to `.github/workflows/ci.yml`.
- Fixed a bug the suite would have caught: `electricity_price_eur_mwh` and other
  secondary `co2_energy` fields were marked required in the Pydantic schema, but free
  live sources (OWID) don't publish them — every live-sourced row was silently failing
  the 95% quality gate and never reaching the database. Made those fields `Optional`
  and fixed NaN-vs-`None` handling in the validator (`app/validation/checks.py`).

## [1.5.0] - Genuinely live CO2/energy data

- Fixed two silent bugs that meant "live mode" was never actually loading live data:
  a filename-routing mismatch in `app/cleaning/clean.py` (live files didn't match the
  cleaner lookup and were skipped), and a raw-column-schema mismatch (OWID's native
  column names never matched our schema).
- Added `app/ingestion/sources.py: fetch_and_merge_co2_energy()`, which fetches OWID
  CO2 + energy data, renames/merges into our schema, and tags `data_quality="official"`.
- `run_all.py` now clears stale raw files before each ingestion run to avoid
  non-deterministic collisions between old and new pulls of the same dataset.
- Added a permanent `.env` (`DATA_MODE=live`) so live mode is the default without
  re-setting an environment variable every session.

## [1.4.0] - R dashboard bug fixes + live/sample data indicator

- Fixed the Climate Risk Map: `addLegend()`/`addCircleMarkers()` were reading a stale
  pre-mutation copy of the data (`d$val` added after the Leaflet proxy snapshot was
  taken), leaving the map blank.
- Replaced `shiny::validate(need(...))` with a custom `safe_validate()` helper
  (`global.R`) after discovering the installed shiny/R build throws a spurious
  `is.character(txt)` error out of `validate()`'s own internals — affected the Country
  Comparison and Forecast Lab tabs.
- Fixed the Scope 1/2/3 emissions treemap: Plotly treemaps require every `parents`
  value to also exist as its own labeled node; added the missing sector-level roots.
- Added tab-memory: the selected sidebar tab now persists across page reloads via
  `localStorage`, since `shiny.autoreload` always restarts on the app's default tab.
- The "Sample / demo data" badge on the Executive Overview tab is now dynamic — it
  reflects the actual `data_quality` of what loaded, instead of always showing the
  sample-data notice regardless of source.

## [1.3.0] - One-command local launch + auto-reload

- Added `api/start_api.bat`: pulls live data only on first run (or with the `refresh`
  argument), otherwise starts instantly; also auto-launches the R dashboard in a
  second window.
- Added `r_dashboard/start_dashboard.bat` with `shiny.autoreload` enabled.
- Enabled `uvicorn --reload` on the API, so both the API and the dashboard now pick up
  code edits automatically without a manual stop/restart.

## [1.2.0] - API moved to a top-level folder

- Moved `python/app/api` to a top-level `api/` folder so the FastAPI service is a
  clearly separate, shared component consumed by the R dashboard, the Azure Function,
  and Docker — not nested inside a generically-named `python/` folder.
- Updated `Dockerfile.api`, `.github/workflows/ci.yml`, the Azure Function, and
  `scripts/hourly_refresh.py` to the new path.

## [1.1.0] - Standalone HTML preview dashboard

- Added `dach_esg_dashboard_preview.html`, a self-contained, zero-install HTML view
  (Chart.js + Leaflet.js via CDN) mirroring every R dashboard tab, with an API-first,
  sample-data-fallback pattern matching `r_dashboard/app/data/load_data.R`.

## [1.0.0] - Initial platform build (Phases 1-11)

- Business scope, architecture, and data source documentation.
- Python data engineering layer: ingestion, cleaning, Pydantic validation, cross-run
  reconciliation ("double-check") gate, SQLite serving layer, FastAPI service.
- Databricks lakehouse notebooks: Bronze -> Silver -> Gold, MLflow forecasting,
  anomaly detection, climate-risk/ESG-readiness scoring.
- R Shiny enterprise dashboard: 10 tabs (incl. a 7-sub-tab Predictor & Forecasting Lab
  and a multi-layer Leaflet climate risk map), bilingual EN/DE.
- AI/LLM layer: Q&A, CSRD readiness assistant, anomaly explanation, ESG report
  summarizer, executive summary generator, risk recommendation engine — prompt
  templates, hallucination-control grounding checks, offline fallback, GDPR-safe design.
- Azure Bicep IaC, Azure Function (hourly ingestion), Docker + docker-compose, GitHub
  Actions CI.
- Full test suite (unit, DB, LLM output quality, security/GDPR, performance, R tests).
- Deployment guide covering local, Docker, Azure, and Databricks.

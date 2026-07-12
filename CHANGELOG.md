# Changelog

All notable changes to this project are documented here. Versioning follows
[Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):
- **MAJOR** — breaking changes (e.g. API contract changes, folder restructures)
- **MINOR** — new features, additive and backward-compatible
- **PATCH** — bug fixes, no new features

Current version: **1.9.1** (see `VERSION`)

## [1.9.1] - Fix CI: python-tests job failing on every push

- `.github/workflows/ci.yml`'s `python-tests` job had a pre-existing bug (present
  since the initial scaffold, unrelated to recent feature work): the "Generate sample
  data" step set `working-directory: .`, which GitHub Actions resolves relative to the
  repo root, overriding (not appending to) the job's `defaults.run.working-directory:
  api`. Since the step's command (`python ../scripts/generate_sample_data.py`) assumed
  it was running from `api/`, it looked one directory too high and failed with
  "No such file or directory" on every CI run. Removed the incorrect override so the
  step correctly inherits the job's `api/` working directory, matching the pattern
  already used correctly in the `data-quality-tests` job.

## [1.9.0] - Fully automatic background data refresh

- The database schema self-heals automatically on every API start (v1.7.0), but the
  *data itself* still needed a manual `start_api.bat refresh` — the root cause of the
  Executive Overview badge repeatedly showing "Sample" even after the pipeline fixes
  in v1.5.0. Added `app/core/scheduler.py`: a background daemon thread that pulls
  fresh data (ingest -> clean -> validate -> reconcile -> load) immediately on API
  startup and every `auto_refresh_interval_seconds` (default 3600s) after that, with
  zero manual commands ever required. Controlled via `AUTO_REFRESH_ENABLED` /
  `AUTO_REFRESH_INTERVAL_SECONDS` in `.env`.
- Migrated `app/api/main.py` off the deprecated `@app.on_event("startup")` API to
  FastAPI's `lifespan` context manager (this sandbox's installed FastAPI 0.139
  flagged the old API as deprecated).

## [1.8.0] - Full EN/DE translation coverage + treemap readability

- Fixed a real gap in the bilingual requirement: only the sidebar/tab labels and a
  handful of top-level outputs were actually wired to the translation system —
  most box titles, chart/series titles, axis labels, and dropdown choices inside
  every module were hardcoded English strings that never changed when switching to
  German. Added ~70 new keys to `lang/translations.R` and routed every module's UI
  text through `t(key, lang())`, including dynamic dropdown re-labeling (via
  `updateSelectInput`/`updatePickerInput`/etc.) for filters like the Climate Risk
  Map's style/layer/view selectors and the Company ESG Input form.
- Fixed the Scope 1/2/3 treemap's unreadable leaf labels (previously
  `"<sector> <scope>"`, e.g. "Real Estate Scope3", overflowing tiny boxes) — leaves
  now show just the scope name with the sector as the parent box, using explicit
  `ids` for correct hierarchy, plus a larger, consistent text size.

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

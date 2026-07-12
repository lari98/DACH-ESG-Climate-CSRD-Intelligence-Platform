# DACH ESG, Climate Risk & CSRD Intelligence Platform

An end-to-end, portfolio-grade reference platform for ESG, climate risk, and CSRD reporting
intelligence across **Germany, Austria, and Switzerland** — built with Python, Databricks,
Azure, R Shiny, and AI/LLM assistance.

| | |
|---|---|
| **Current version** | 1.9.0 |
| **Version history** | [`CHANGELOG.md`](./CHANGELOG.md) — what changed in every release |
| **Version source of truth** | [`VERSION`](./VERSION) — also returned live by the API at `GET /health` |
| **Business case, target users, KPIs** | [`docs/01_business_scope.md`](./docs/01_business_scope.md) |

## Repository Structure

```
DACH-ESG-Climate-CSRD-Intelligence-Platform/
├── docs/                     Business scope, architecture, data sources, freshness policy
├── data/
│   ├── raw/                  Immutable landing zone (Bronze-equivalent, local mode)
│   ├── cleaned/               Cleaned/validated output (Silver-equivalent, local mode)
│   └── sample/                Generated offline demo dataset (data_quality = "sample")
├── api/                      FastAPI service + ingestion/cleaning/validation/AI (Phase 4 & 8)
│   └── app/
│       ├── core/              config, logging
│       ├── ingestion/          live source connectors + orchestrator
│       ├── cleaning/           standardization layer
│       ├── validation/         pydantic schemas, quality gate, double-check reconciliation
│       ├── db/                 SQLAlchemy models + load routine
│       ├── api/                FastAPI app (serving + AI endpoints)
│       └── ai/                 LLM client + ESG/CSRD assistant (Azure OpenAI or local fallback)
├── databricks/notebooks/     Bronze → Silver → Gold Delta Lake pipeline + MLflow ML (Phase 5)
├── r_dashboard/               Enterprise bilingual (EN/DE) R Shiny dashboard (Phase 6)
│   └── app/
│       ├── modules/            One file per dashboard tab (10 tabs + 7 forecast sub-tabs)
│       ├── lang/                EN/DE translation dictionary
│       ├── data/                 API client / local CSV fallback
│       └── www/                  Enterprise DACH CSS theme
├── data_quality_tests/        Standalone source/data QA suite (15 categories - see its README)
├── azure/                     Bicep IaC + Azure Function (hourly ingestion timer trigger)
├── docker/                    Dockerfiles + docker-compose for API + dashboard
├── .github/workflows/        CI: Python tests, R syntax check, Docker build
└── scripts/                   generate_sample_data.py, hourly_refresh.py
```

## Quick Start (Local, Free)

```bash
# 1. Generate the offline sample dataset
python scripts/generate_sample_data.py

# 2. Python pipeline: ingest -> clean -> validate/double-check -> load into SQLite
cd api
pip install -r requirements.txt
python -m app.ingestion.run_all
python -m app.cleaning.clean
python -m app.db.session

# 3. Start the API
uvicorn app.api.main:app --reload --port 8000
# docs at http://localhost:8000/docs

# 4. Start the dashboard (separate terminal)
cd ../r_dashboard
Rscript install_packages.R
R -e "shiny::runApp('app', port = 3838)"
```

Or with Docker: `docker compose -f docker/docker-compose.yml up --build`.

**Fastest path (Windows, one command):** `api\start_api.bat` — pulls live data only on
first run (or when passed `refresh`), otherwise starts instantly, and auto-launches the
R dashboard in a second window. Both the API and dashboard auto-reload on code changes
and the database schema auto-migrates itself on every restart — see `CHANGELOG.md` 1.3.0
and 1.7.0.

## API Reference

Base URL: `http://localhost:8000` (local) — interactive docs always available live at
`/docs`. All endpoints are free to call locally; no API key required.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check — returns `status`, `version`, `environment`, `data_mode` |
| GET | `/api/v1/co2-energy` | CO2/energy records. Query params: `country`, `year_from`, `year_to` |
| GET | `/api/v1/climate-risk` | Regional climate risk scores. Query param: `country` |
| GET | `/api/v1/companies` | Company ESG records. Query params: `country`, `sector` |
| GET | `/api/v1/companies/{company_id}` | Single company by ID (404 if not found) |
| POST | `/api/v1/ai/ask` | Free-form Q&A over the loaded data. Body: `{question, lang}` |
| POST | `/api/v1/ai/csrd-readiness` | CSRD readiness summary for a company. Body: `{company_id, lang}` |
| POST | `/api/v1/ai/anomaly-explanation` | Explains a detected anomaly. Body: `{column, relative_change, lang}` |
| POST | `/api/v1/ai/summarize-report` | Summarizes pasted ESG report text. Body: `{report_text, lang}` |
| POST | `/api/v1/ai/executive-summary` | Executive summary from a KPI dict. Body: `{kpis, lang}` |
| POST | `/api/v1/ai/risk-recommendation` | Risk-mitigation recommendations. Body: `{risk_profile, lang}` |

`/summarize-report`, `/executive-summary`, and `/risk-recommendation` return a
`GroundedResponse`: `{text, grounded, warning}`, where `grounded=false` means the
hallucination-control check couldn't fully verify the answer against source data
(`/ask` and `/csrd-readiness`/`/anomaly-explanation` return simpler `{answer}` /
`{summary}` shapes) — see `docs/05_ai_llm_design.md`.

## Cost & Data Freshness

Every wired data source is free with no API key (Our World in Data, Eurostat, ENTSO-E). See
`docs/04_data_freshness_and_accuracy.md` for the honest breakdown of what can genuinely be
hourly/real-time versus official annual statistics, and how the pipeline's double-check
reconciliation gate protects against bad pulls.

## Testing

| Suite | Location | Run with | Covers |
|---|---|---|---|
| Application tests | `api/tests/` | `cd api && pytest -q` | Cleaning, validation, reconciliation, DB, API endpoints, AI grounding, security/GDPR, performance |
| Data quality tests | `data_quality_tests/` | `pytest data_quality_tests -v` | 15 categories: source availability, connection, auth, schema, columns, types, record counts, freshness, completeness, duplicates, nulls, encoding, timestamps, referential integrity, PII classification — see its own `README.md` |
| R dashboard tests | `r_dashboard/tests/` | `Rscript -e "testthat::test_dir('tests/testthat')"` (from `r_dashboard/`) | Translation dictionary, forecast helper functions, app smoke test (`shinytest2`) |
| R syntax check | all `r_dashboard/**/*.R` | runs automatically in CI | Every `.R` file parses without error |

All four run automatically in CI on every push (`.github/workflows/ci.yml`): `python-tests`,
`data-quality-tests`, `r-lint`, and `docker-build` jobs.

## License / Attribution

Public data sources: Our World in Data (CC BY), Eurostat (free re-use with attribution).
Company ESG data in `data/sample` is entirely synthetic and for demonstration only.

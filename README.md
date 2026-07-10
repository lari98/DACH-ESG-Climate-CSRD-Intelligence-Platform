# DACH ESG, Climate Risk & CSRD Intelligence Platform

An end-to-end, portfolio-grade reference platform for ESG, climate risk, and CSRD reporting
intelligence across **Germany, Austria, and Switzerland** — built with Python, Databricks,
Azure, R Shiny, and AI/LLM assistance.

See `docs/01_business_scope.md` for the full business case, target users, and KPIs.

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

## Cost & Data Freshness

Every wired data source is free with no API key (Our World in Data, Eurostat, ENTSO-E). See
`docs/04_data_freshness_and_accuracy.md` for the honest breakdown of what can genuinely be
hourly/real-time versus official annual statistics, and how the pipeline's double-check
reconciliation gate protects against bad pulls.

## Testing

```bash
cd api && pytest -q          # 10 tests: cleaning, validation, reconciliation, API, AI
```

R files are syntax-checked in CI (`.github/workflows/ci.yml`); a full `shinytest2` suite is
the natural next step once deployed to an R environment.

## License / Attribution

Public data sources: Our World in Data (CC BY), Eurostat (free re-use with attribution).
Company ESG data in `data/sample` is entirely synthetic and for demonstration only.

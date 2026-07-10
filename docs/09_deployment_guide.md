# Phase 11 — Deployment Guide

## Repository layout (post Phase 11 restructure)

The FastAPI backend now lives in its own top-level `api/` folder — it is the single shared
service consumed by the R dashboard (`ESG_API_BASE`), the Azure Function (`azure/functions/`),
and Docker (`docker/Dockerfile.api`). Nothing else in the repo talks to a database directly;
every consumer goes through this one API.

```
DACH-ESG-Climate-CSRD-Intelligence-Platform/
├── api/                 <- shared FastAPI service (moved out of python/ in Phase 11)
├── r_dashboard/         <- consumes api/ over HTTP (ESG_API_BASE env var)
├── databricks/          <- Lakehouse notebooks (independent of api/, writes to Delta/Gold tables)
├── azure/functions/     <- hourly_ingestion timer trigger imports api/app directly
├── docker/              <- Dockerfile.api builds from api/, Dockerfile.shiny builds the dashboard
└── docs/
```

## 1. Local deployment (free, no cloud account)

```bash
python scripts/generate_sample_data.py
cd api && pip install -r requirements.txt
python -m app.ingestion.run_all && python -m app.cleaning.clean && python -m app.db.session
uvicorn app.api.main:app --reload --port 8000     # API at :8000, docs at /docs

# separate terminal
cd r_dashboard && Rscript install_packages.R
R -e "shiny::runApp('app', port = 3838)"          # dashboard at :3838
```

Set `ESG_API_BASE=http://localhost:8000` (default) so the R dashboard finds the API.

## 2. Docker deployment

```bash
docker compose -f docker/docker-compose.yml up --build
```

Brings up two containers: `api` (FastAPI, port 8000) and `dashboard` (Shiny, port 3838), wired
together via the `ESG_API_BASE=http://api:8000` environment variable set in
`docker/docker-compose.yml`. No other setup required — sample data mode is the default.

## 3. Azure deployment

1. **Provision infrastructure**: `az deployment group create -g <resource-group> -f azure/bicep/main.bicep -p environmentName=prod` — creates Storage (raw/bronze/silver/gold containers), Key Vault, Azure SQL, a Function App, and a Log Analytics workspace, all in `germanywestcentral` by default for EU data residency (see `docs/02_architecture.md`).
2. **Store secrets in Key Vault**, not in `.env`: `AZURE_SQL_CONNECTION_STRING`, `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_OPENAI_API_KEY`. Grant the API's managed identity `get`/`list` access to the vault; the app reads these via `azure_key_vault_url` in `api/app/core/config.py` (extend `get_settings()` to pull from Key Vault when `ENVIRONMENT=azure` — see the TODO-style comment pattern already used for local vs. Azure switching).
3. **Deploy the API** as an Azure Web App / Container App from `docker/Dockerfile.api`, or as an Azure Function if you prefer a serverless model — the FastAPI app is ASGI-compatible with either via `azure-functions` + `asgi` adapters.
4. **Deploy the hourly ingestion Function**: `azure/functions/hourly_ingestion/` is ready to publish as-is (`func azure functionapp publish <app-name>`); its timer trigger (`function.json`, schedule `0 0 * * * *`) calls the same `ingest -> clean -> validate -> reconcile -> load` pipeline as local mode.
5. **Point the dashboard at the Azure API**: set `ESG_API_BASE` to the deployed API's URL wherever Shiny is hosted (Shiny Server, Posit Connect, or a container).

## 4. Databricks deployment

1. Import the notebooks under `databricks/notebooks/` into a Databricks workspace (Repos or manual import), preserving the `bronze/ -> silver/ -> gold/ -> ml/` folder structure.
2. Create a Databricks Workflow with four tasks in sequence: `01_bronze_ingest` → `01_silver_transform` → `01_gold_kpis` → (`01_forecasting_mlflow`, `02_anomaly_detection`, `03_risk_esg_scoring` run in parallel, all downstream of Gold).
3. Set the `raw_path` widget on the Bronze notebook to the mounted Azure Blob `raw` container (`/mnt/dach-esg/raw`), matching the Storage account from the Bicep deployment.
4. Schedule the Workflow (e.g. hourly or daily, matching your data cadence — see `docs/04_data_freshness_and_accuracy.md`) and optionally sync Gold tables to Azure SQL for the API to serve, via a Databricks-to-SQL export step or Azure Data Factory.
5. MLflow experiments/models registered by the ML notebooks are visible in the workspace's MLflow tracking UI and Model Registry — promote a model to `Production` stage once validated (see `docs/06_ml_forecasting_scoring.md` for evaluation metrics to check first).

## 5. Environment variables reference

All settings are read via `api/app/core/config.py` (`pydantic-settings`, `.env`-file aware).
See `.env.example` at the repo root for the full list. Key ones:

| Variable | Local default | Azure |
|---|---|---|
| `ENVIRONMENT` | `local` | `azure` |
| `DATA_MODE` | `sample` | `live` |
| `DATABASE_URL` | `sqlite:///data/esg_platform.db` | Azure SQL connection string (from Key Vault) |
| `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_API_KEY` | unset (offline AI fallback) | set once Azure OpenAI is provisioned |
| `ESG_API_BASE` (R dashboard only) | `http://localhost:8000` | deployed API URL |

## 6. Key Vault usage

Never commit real secrets — `.env` is git-ignored (`.gitignore`) and `.env.example` documents
the shape without values. In Azure mode, `api/app/core/config.py`'s `azure_key_vault_url`
setting is the integration point: extend `Settings` with an Azure Identity + Key Vault SDK call
(`azure-identity`, `azure-keyvault-secrets`) so secrets are pulled at startup rather than passed
as plain environment variables, using the deployed resource's managed identity for auth (no
credentials stored anywhere in code or config).

## 7. Monitoring & logging

- **Application logs**: every module uses the shared `get_logger()` helper
  (`api/app/core/logging.py`), which formats consistently and is ready to ship to Azure Monitor /
  Log Analytics by attaching the `opencensus-ext-azure` or `azure-monitor-opentelemetry` handler
  in production (the Bicep template already provisions a Log Analytics workspace for this).
- **Request logging**: the FastAPI app logs every request's method, path, status, and duration
  via its `log_requests` middleware (`api/app/api/main.py`) — visible in stdout locally and
  forwardable to Azure Monitor in the cloud.
- **Pipeline observability**: `scripts/hourly_refresh.py` and the Azure Function both log
  ingestion/cleaning/load counts and any reconciliation anomalies withheld — set up an Azure
  Monitor alert rule on the Function App's failure count and on log entries containing
  "reconciliation flagged" for proactive data-quality alerting.
- **MLflow**: every forecasting/scoring run's metrics are queryable via the Databricks MLflow UI
  — a Databricks Workflow failure or a metric drift (e.g. MAE trending up) is the ML-side signal
  to watch, ahead of a full model-monitoring setup (e.g. Evidently AI) as a future enhancement.

## 8. Cost control

- **Default to $0**: `DATA_MODE=sample` + no `AZURE_OPENAI_*` vars means the entire stack (API,
  dashboard, tests) runs free, locally or in Docker, with zero Azure spend.
- **Azure OpenAI**: the only line item with real per-call cost. The offline fallback in
  `api/app/ai/llm_client.py` means this is opt-in, not required — enable it only once you want
  live LLM answers, and consider a low-cost deployment tier (e.g. `gpt-4o-mini`, already the
  default deployment name in `config.py`) plus a token/response cap (`max_tokens=400` is already
  set on every call).
- **Azure Function consumption plan** (`Y1`/Dynamic SKU in the Bicep template): pay-per-execution,
  effectively free at hourly-trigger volume (well under the monthly free grant).
- **Storage/SQL**: the Bicep template uses `Standard_LRS` storage and `Basic` tier SQL — the
  cheapest production-viable SKUs; scale up only if the dashboard's user count or data volume
  requires it.
- **Databricks**: the biggest potential cost center — use a small/spot-instance cluster with
  auto-termination (e.g. 15-30 min idle timeout) for the scheduled Workflow, since these are
  short, infrequent batch jobs, not an always-on cluster.

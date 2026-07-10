# Phase 2 — Architecture

## End-to-End Data Flow

```
Public Sources (Eurostat, Our World in Data, national stats offices)
        │
        ▼
[1] INGESTION            python/app/ingestion  (requests + pandas, scheduled)
        │  raw CSV/JSON  → data/raw/  (immutable landing zone)
        ▼
[2] STORAGE (cloud)      Azure Blob Storage (raw container)  /  local: data/raw
        ▼
[3] TRANSFORMATION       Databricks Lakehouse
        │   Bronze  → raw ingested, schema-on-read, audit columns
        │   Silver  → cleaned, validated, conformed (country/region codes, units)
        │   Gold    → business-level KPI tables (CO2, energy mix, ESG scores, climate risk)
        ▼
[4] SERVING LAYER        Azure SQL / PostgreSQL (Gold tables synced) + FastAPI (python/app/api)
        ▼
[5] ML / AI              MLflow-tracked forecasting (Prophet/ARIMA) + anomaly detection (PySpark/Sklearn)
        │                Azure OpenAI: summarization, CSRD assistant, NL Q&A, anomaly explanation
        ▼
[6] DASHBOARD             R Shiny (r_dashboard/) — reads from FastAPI / Azure SQL / Gold Delta tables
        ▼
[7] REPORT EXPORT          rmarkdown → PDF/HTML/Excel, CSRD-readiness report, audit trail export
```

## Azure Architecture

| Service | Role |
|---|---|
| **Azure Blob Storage** | Raw + curated data lake landing zone (`raw`, `bronze`, `silver`, `gold` containers) |
| **Azure Databricks** | Lakehouse compute: PySpark ETL, Delta Lake, MLflow |
| **Azure SQL / PostgreSQL Flexible Server** | Serving layer for Gold KPI tables consumed by API/dashboard |
| **Azure Functions** | Scheduled ingestion triggers, lightweight ETL glue, webhook endpoints |
| **Azure OpenAI Service** | LLM backend for ESG summarization, CSRD assistant, anomaly explanation, NL Q&A (bilingual EN/DE) |
| **Azure Key Vault** | Secrets: DB connection strings, API keys, OpenAI keys — never stored in code/config |
| **Azure Monitor / Log Analytics** | Pipeline observability, alerting on ingestion/data-quality failures |
| **Azure Active Directory** | Service principal auth for Databricks ↔ Storage ↔ SQL, RBAC |

Diagram source: `docs/diagrams/architecture.mmd` (Mermaid).

## Databricks Lakehouse Architecture (Medallion)

- **Bronze** (`databricks/notebooks/bronze`): raw ingestion as Delta tables, append-only, `_ingested_at`,
  `_source_file` audit columns, minimal transformation.
- **Silver** (`databricks/notebooks/silver`): typed, deduplicated, country/region codes standardized
  (ISO-3166, NUTS codes for DE/AT/CH regions), unit-normalized (Mt CO₂, GWh, %).
- **Gold** (`databricks/notebooks/gold`): business aggregates — `gold_co2_emissions`,
  `gold_energy_mix`, `gold_renewable_share`, `gold_esg_scores`, `gold_climate_risk`, `gold_scope_emissions`.
- **ML** (`databricks/notebooks/ml`): MLflow-tracked forecasting experiments + anomaly detection,
  registered models promoted to `Staging`/`Production` in the MLflow Model Registry.
- Data quality checks run at each layer boundary (row counts, null thresholds, range checks,
  referential integrity of country/region codes) — see `python/app/validation`.

## Local Development Option (Free / Low-Cost)

The project is fully runnable without an Azure subscription:

- **Storage** → local `data/raw` / `data/cleaned` folders instead of Blob Storage.
- **Database** → SQLite (via SQLAlchemy) instead of Azure SQL/PostgreSQL.
- **Lakehouse** → local Delta Lake via `delta-spark` + local PySpark, or plain pandas/parquet for a
  lighter-weight substitute of the Bronze/Silver/Gold notebooks.
- **AI/LLM** → `python/app/ai` supports a local/offline fallback (rule-based + template summaries) when
  no `AZURE_OPENAI_*` environment variables are set, so the AI panels still work with zero cloud cost.
- **Dashboard** → R Shiny runs locally via `shiny::runApp("r_dashboard/app")`, reading from SQLite/CSV.

Switching between local and Azure is controlled entirely through `python/app/core/config.py`
environment variables (`ENVIRONMENT=local|azure`) — no code changes required.

## Security & GDPR Design

- **No personal data by design**: all datasets are aggregate national/regional statistics or
  company-level ESG figures (not individual data) — minimizes GDPR surface area from the start.
- **Secrets management**: all credentials via Azure Key Vault in cloud mode, `.env` (git-ignored) in
  local mode; `python/app/core/config.py` never hardcodes secrets.
- **Least privilege**: Azure AD service principals scoped per-service (Databricks storage access,
  Function App DB access) rather than shared credentials.
- **Data residency**: Azure resources deployed to `westeurope`/`germanywestcentral` regions to keep
  data within EU/DACH jurisdiction.
- **Audit trail**: Bronze layer retains immutable raw history; Gold tables carry `_updated_at` and
  `_source_run_id` for full lineage back to the ingestion run (supports CSRD audit requirements).
- **Company ESG input data**: user-submitted company data (Phase 6 "Company ESG Input") is validated,
  stored separately from public reference data, and clearly labeled as user-supplied vs. official
  source in the dashboard and exports.

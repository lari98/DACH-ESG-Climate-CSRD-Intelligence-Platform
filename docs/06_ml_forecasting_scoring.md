# Phase 8 — Forecasting & ML Scoring

All models are trained and tracked in Databricks notebooks under `databricks/notebooks/ml/`,
logged to MLflow (params, metrics, model artifact, registered model name).

| Capability | Notebook | Registered model(s) |
|---|---|---|
| CO2 emissions forecasting | `01_forecasting_mlflow.py` | `dach_esg_co2_emissions_mt_{country}` |
| Renewable energy forecasting | `01_forecasting_mlflow.py` | `dach_esg_renewable_share_pct_{country}` |
| Electricity price / trend forecasting | `01_forecasting_mlflow.py` (Phase 8 addition) | `dach_esg_electricity_price_eur_mwh_{country}` |
| Anomaly detection | `02_anomaly_detection.py` | `dach_esg_anomaly_detector` |
| Climate risk scoring | `03_risk_esg_scoring.py` (Phase 8 addition) | `dach_esg_climate_risk_score` |
| ESG readiness scoring | `03_risk_esg_scoring.py` (Phase 8 addition) | `dach_esg_readiness_score` |

## Model evaluation metrics

- **Forecasting models** (CO2, renewable share, electricity price): MAE on a held-out 20% test
  split, logged per (country, metric) run; a consolidated `gold_model_evaluation` Delta table
  adds MAPE/RMSE for easier cross-run comparison (added in `01_forecasting_mlflow.py`, "Model
  Evaluation Metrics" cell).
- **Anomaly detection**: `n_anomalies_flagged` logged per run; IsolationForest contamination
  parameter (0.1) is a tracked hyperparameter so sensitivity can be tuned and compared across runs.
- **Climate risk scoring**: MAE / RMSE / R² against the existing composite score, plus the
  learned feature weights are printed and loggable as an artifact — kept as an interpretable
  linear model (not a black box) so a reviewer can see exactly how much each sub-risk
  (physical/transition/flood/heat) contributes, which matters for audit-friendliness.
- **ESG readiness scoring**: MAE / RMSE / R² against the labeled `esg_readiness_score`, letting
  the model estimate readiness for companies with incomplete self-reported scores based on
  reporting-gap count and total emissions.

## Why linear/explainable models, not deep learning

Given the dataset scale (annual country-level series, ~40 sample companies) and the audit
context (CSRD-adjacent reporting), simple, explainable models (linear regression, isolation
forest) are the right choice: they're fast to retrain hourly (see
`docs/04_data_freshness_and_accuracy.md`), cheap to run without GPU infrastructure, and every
coefficient/threshold can be explained to a non-technical stakeholder or auditor. The MLflow
Model Registry (`Staging`/`Production` stages) is the natural place to promote a more
sophisticated model (Prophet/ARIMA/gradient boosting) later without changing how the API or
dashboard consumes forecasts — see `docs/02_architecture.md`.

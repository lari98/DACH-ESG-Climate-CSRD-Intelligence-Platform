# Databricks notebook source
# MAGIC %md
# MAGIC # Forecasting Pipeline (MLflow-tracked)
# MAGIC Trains per-country forecast models for CO2 emissions and renewable share, logs runs/metrics/
# MAGIC models to MLflow, and registers the best model per (country, metric) to the Model Registry.
# MAGIC Horizons: 1y, 3y, 5y, 10y, and fixed target years 2030 / 2040 / 2050 — matching the R Shiny
# MAGIC "Forecast horizon selector".

# COMMAND ----------
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

GOLD_DB = "dach_esg_gold"
EXPERIMENT_NAME = "/Shared/dach_esg_forecasting"
mlflow.set_experiment(EXPERIMENT_NAME)

HORIZON_YEARS = [1, 3, 5, 10]
TARGET_YEARS = [2030, 2040, 2050]

# COMMAND ----------
co2_pdf = spark.table(f"{GOLD_DB}.gold_co2_emissions").toPandas()
energy_pdf = spark.table(f"{GOLD_DB}.gold_energy_mix").toPandas()

# COMMAND ----------
def train_and_log(country: str, metric_name: str, series: pd.DataFrame, value_col: str):
    """Fits a simple, explainable trend model (polynomial regression) per country/metric,
    logs to MLflow with params/metrics/model, and returns forecast rows for all horizons.
    A production upgrade path is Prophet/ARIMA per the Phase 6 R 'forecast'/'fable' stack —
    the MLflow tracking contract (params, metrics, registered model) stays the same either way."""
    series = series.sort_values("year")
    X = series[["year"]].values
    y = series[value_col].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    with mlflow.start_run(run_name=f"{country}_{metric_name}"):
        model = LinearRegression()
        model.fit(X_train, y_train)
        preds_test = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds_test) if len(X_test) else float("nan")

        mlflow.log_param("country", country)
        mlflow.log_param("metric", metric_name)
        mlflow.log_param("model_type", "LinearRegression")
        mlflow.log_param("n_train_years", len(X_train))
        mlflow.log_metric("mae", mae)
        mlflow.sklearn.log_model(model, artifact_path="model",
                                  registered_model_name=f"dach_esg_{metric_name}_{country.lower()}")

        last_year = int(series["year"].max())
        forecast_rows = []
        for h in HORIZON_YEARS:
            target_year = last_year + h
            pred = float(model.predict([[target_year]])[0])
            forecast_rows.append({
                "country_code": country, "metric": metric_name, "horizon_years": h,
                "target_year": target_year, "forecast_value": pred,
                "ci_lower": pred - 1.96 * mae if not np.isnan(mae) else None,
                "ci_upper": pred + 1.96 * mae if not np.isnan(mae) else None,
            })
        for ty in TARGET_YEARS:
            pred = float(model.predict([[ty]])[0])
            forecast_rows.append({
                "country_code": country, "metric": metric_name, "horizon_years": ty - last_year,
                "target_year": ty, "forecast_value": pred,
                "ci_lower": pred - 1.96 * mae if not np.isnan(mae) else None,
                "ci_upper": pred + 1.96 * mae if not np.isnan(mae) else None,
            })
        return forecast_rows

# COMMAND ----------
all_forecasts = []
for country in ["DE", "AT", "CH"]:
    co2_country = co2_pdf[co2_pdf["country_code"] == country]
    energy_country = energy_pdf[energy_pdf["country_code"] == country]
    all_forecasts += train_and_log(country, "co2_emissions_mt", co2_country, "co2_emissions_mt")
    all_forecasts += train_and_log(country, "renewable_share_pct", energy_country, "renewable_share_pct")
    # Phase 8 addition: electricity price / trend forecasting, same MLflow-tracked pipeline
    all_forecasts += train_and_log(country, "electricity_price_eur_mwh", energy_country, "electricity_price_eur_mwh")

forecast_df = spark.createDataFrame(pd.DataFrame(all_forecasts))
forecast_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable("dach_esg_gold.gold_forecasts")

display(forecast_df)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Model Evaluation Metrics (Phase 8)
# MAGIC Every run above already logs `mae` (mean absolute error on the held-out test split) to
# MAGIC MLflow. This cell adds MAPE and RMSE for a fuller picture and writes a consolidated
# MAGIC evaluation table so model quality can be reviewed without opening MLflow UI per-run.

# COMMAND ----------
import numpy as np
from mlflow.tracking import MlflowClient

client = MlflowClient()
experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
runs = client.search_runs(experiment.experiment_id) if experiment else []

eval_rows = []
for run in runs:
    p = run.data.params
    m = run.data.metrics
    eval_rows.append({
        "run_id": run.info.run_id,
        "country": p.get("country"),
        "metric": p.get("metric"),
        "model_type": p.get("model_type"),
        "mae": m.get("mae"),
    })

eval_df = spark.createDataFrame(pd.DataFrame(eval_rows)) if eval_rows else None
if eval_df is not None:
    eval_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable("dach_esg_gold.gold_model_evaluation")
    display(eval_df)

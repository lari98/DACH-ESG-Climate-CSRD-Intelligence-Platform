# Databricks notebook source
# MAGIC %md
# MAGIC # Phase 8 — Climate Risk Scoring & ESG Readiness Scoring (MLflow-tracked)
# MAGIC Two composite scoring models, both logged to MLflow with evaluation metrics:
# MAGIC 1. **Climate risk score** — weighted composite of physical/transition/flood/heat sub-scores,
# MAGIC    validated against a held-out split using a simple weighted-linear model so weights are
# MAGIC    interpretable (audit-friendly, per the project's "consulting-grade / audit-friendly"
# MAGIC    requirement) rather than a black-box ensemble.
# MAGIC 2. **ESG readiness score** — regression from Scope 1/2/3 intensity + reporting-gap count to
# MAGIC    the labeled esg_readiness_score, so new/unlabeled companies can get an estimated score.

# COMMAND ----------
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

GOLD_DB = "dach_esg_gold"
mlflow.set_experiment("/Shared/dach_esg_risk_and_readiness_scoring")

def eval_metrics(y_true, y_pred):
    return {
        "mae": mean_absolute_error(y_true, y_pred),
        "rmse": mean_squared_error(y_true, y_pred, squared=False),
        "r2": r2_score(y_true, y_pred) if len(y_true) > 1 else float("nan"),
    }

# COMMAND ----------
# MAGIC %md ## 1. Climate Risk Scoring

# COMMAND ----------
risk_pdf = spark.table(f"{GOLD_DB}.gold_climate_risk").toPandas()

X = risk_pdf[["physical_risk_score", "transition_risk_score", "flood_risk_score", "heat_stress_score"]]
y = risk_pdf["composite_climate_risk_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

with mlflow.start_run(run_name="climate_risk_scoring"):
    model = LinearRegression(positive=True)  # positive weights -> interpretable "higher sub-risk = higher composite"
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = eval_metrics(y_test, preds)

    mlflow.log_param("model_type", "LinearRegression(positive=True)")
    mlflow.log_param("features", list(X.columns))
    for k, v in metrics.items():
        mlflow.log_metric(k, v)
    mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="dach_esg_climate_risk_score")

    weights = dict(zip(X.columns, model.coef_))
    print("Climate risk score weights (interpretable):", weights)
    print("Eval metrics:", metrics)

risk_pdf["predicted_risk_score"] = model.predict(X)
spark.createDataFrame(risk_pdf).write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_climate_risk_scored")

# COMMAND ----------
# MAGIC %md ## 2. ESG Readiness Scoring

# COMMAND ----------
company_pdf = spark.table(f"{GOLD_DB}.gold_esg_scores").toPandas()
scope_pdf = spark.table(f"{GOLD_DB}.gold_scope_emissions").toPandas()[["company_id", "total_tco2e"]]
merged = company_pdf.merge(scope_pdf, on="company_id", how="left").dropna(subset=["total_tco2e"])

Xr = merged[["reporting_gaps_count", "total_tco2e"]]
yr = merged["esg_readiness_score"]
Xr_train, Xr_test, yr_train, yr_test = train_test_split(Xr, yr, test_size=0.25, random_state=42)

with mlflow.start_run(run_name="esg_readiness_scoring"):
    model2 = LinearRegression()
    model2.fit(Xr_train, yr_train)
    preds2 = model2.predict(Xr_test)
    metrics2 = eval_metrics(yr_test, preds2)

    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_param("features", list(Xr.columns))
    for k, v in metrics2.items():
        mlflow.log_metric(k, v)
    mlflow.sklearn.log_model(model2, artifact_path="model", registered_model_name="dach_esg_readiness_score")

    print("ESG readiness scoring eval metrics:", metrics2)

merged["predicted_esg_readiness_score"] = model2.predict(Xr)
spark.createDataFrame(merged).write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_esg_readiness_scored")

display(spark.table(f"{GOLD_DB}.gold_esg_readiness_scored"))

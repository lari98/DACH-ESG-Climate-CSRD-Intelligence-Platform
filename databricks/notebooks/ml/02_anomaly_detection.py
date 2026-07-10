# Databricks notebook source
# MAGIC %md
# MAGIC # Anomaly Detection Pipeline (MLflow-tracked)
# MAGIC Flags year-over-year jumps in CO2/energy/climate-risk series that are statistically unusual,
# MAGIC using an IsolationForest per country over engineered YoY-delta features. Anomalies feed the
# MAGIC AI "anomaly explanation" panel in the dashboard (Phase 8).

# COMMAND ----------
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import IsolationForest

GOLD_DB = "dach_esg_gold"
mlflow.set_experiment("/Shared/dach_esg_anomaly_detection")

# COMMAND ----------
co2_pdf = spark.table(f"{GOLD_DB}.gold_co2_emissions").toPandas().sort_values(["country_code", "year"])
energy_pdf = spark.table(f"{GOLD_DB}.gold_energy_mix").toPandas().sort_values(["country_code", "year"])

merged = co2_pdf.merge(energy_pdf, on=["country_code", "year"], suffixes=("", "_e"))
merged["co2_yoy_pct"] = merged.groupby("country_code")["co2_emissions_mt"].pct_change() * 100
merged["renew_yoy_pp"] = merged.groupby("country_code")["renewable_share_pct"].diff()
merged = merged.dropna(subset=["co2_yoy_pct", "renew_yoy_pp"])

# COMMAND ----------
features = merged[["co2_yoy_pct", "renew_yoy_pp"]]

with mlflow.start_run(run_name="isolation_forest_anomaly_detection"):
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(features)
    merged["anomaly_score"] = model.decision_function(features)
    merged["is_anomaly"] = model.predict(features) == -1

    mlflow.log_param("model_type", "IsolationForest")
    mlflow.log_param("contamination", 0.1)
    mlflow.log_metric("n_anomalies_flagged", int(merged["is_anomaly"].sum()))
    mlflow.sklearn.log_model(model, artifact_path="model",
                              registered_model_name="dach_esg_anomaly_detector")

anomalies_df = spark.createDataFrame(
    merged[["country_code", "year", "co2_yoy_pct", "renew_yoy_pp", "anomaly_score", "is_anomaly"]]
)
anomalies_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_anomalies")

display(anomalies_df.filter("is_anomaly = true"))

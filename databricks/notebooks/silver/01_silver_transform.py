# Databricks notebook source
# MAGIC %md
# MAGIC # Silver — Cleaned & Conformed
# MAGIC Types, dedupes, standardizes units/codes, and runs data-quality checks before promotion
# MAGIC to Gold. Mirrors the logic in `python/app/cleaning` + `python/app/validation` so local and
# MAGIC Databricks pipelines agree on business rules.

# COMMAND ----------
from pyspark.sql import functions as F
from pyspark.sql.window import Window

BRONZE_DB = "dach_esg_bronze"
SILVER_DB = "dach_esg_silver"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {SILVER_DB}")

VALID_COUNTRIES = ["DE", "AT", "CH"]

# COMMAND ----------
# MAGIC %md ## co2_energy

# COMMAND ----------
co2 = spark.table(f"{BRONZE_DB}.bronze_co2_energy")

co2_silver = (
    co2
    .withColumn("country_code", F.upper(F.trim("country_code")))
    .filter(F.col("country_code").isin(VALID_COUNTRIES))
    .withColumn("year", F.col("year").cast("int"))
    .withColumn("renewable_share_pct", F.least(F.greatest(F.col("renewable_share_pct"), F.lit(0.0)), F.lit(100.0)))
    .withColumn("fossil_share_pct", F.least(F.greatest(F.col("fossil_share_pct"), F.lit(0.0)), F.lit(100.0)))
    .withColumn("nuclear_share_pct", F.least(F.greatest(F.col("nuclear_share_pct"), F.lit(0.0)), F.lit(100.0)))
    .dropna(subset=["country_code", "year", "co2_emissions_mt"])
)

# dedupe: keep latest ingested row per (country, year)
w = Window.partitionBy("country_code", "year").orderBy(F.col("_ingested_at").desc())
co2_silver = (
    co2_silver.withColumn("_rn", F.row_number().over(w))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)

co2_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{SILVER_DB}.silver_co2_energy")
print(f"silver_co2_energy: {co2_silver.count()} rows")

# COMMAND ----------
# MAGIC %md ## regional_climate_risk

# COMMAND ----------
risk = spark.table(f"{BRONZE_DB}.bronze_regional_climate_risk")

risk_silver = (
    risk
    .withColumn("country_code", F.upper(F.trim("country_code")))
    .withColumn("region", F.trim("region"))
    .filter(F.col("country_code").isin(VALID_COUNTRIES))
    .dropna(subset=["country_code", "region"])
)
for c in ["physical_risk_score", "transition_risk_score", "flood_risk_score",
          "heat_stress_score", "composite_climate_risk_score"]:
    risk_silver = risk_silver.withColumn(c, F.least(F.greatest(F.col(c), F.lit(0.0)), F.lit(10.0)))

w2 = Window.partitionBy("country_code", "region").orderBy(F.col("_ingested_at").desc())
risk_silver = (
    risk_silver.withColumn("_rn", F.row_number().over(w2))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)

risk_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{SILVER_DB}.silver_regional_climate_risk")
print(f"silver_regional_climate_risk: {risk_silver.count()} rows")

# COMMAND ----------
# MAGIC %md ## company_esg

# COMMAND ----------
company = spark.table(f"{BRONZE_DB}.bronze_company_esg")

company_silver = (
    company
    .withColumn("country_code", F.upper(F.trim("country_code")))
    .filter(F.col("country_code").isin(VALID_COUNTRIES))
    .dropna(subset=["company_id", "country_code"])
    .dropDuplicates(["company_id"])
)

company_silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{SILVER_DB}.silver_company_esg")
print(f"silver_company_esg: {company_silver.count()} rows")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Data Quality Gate
# MAGIC Fails the job (raises) if any table's null-rate on key columns exceeds 5%, enforcing the same
# MAGIC 95% pass-rate gate used in the Python pipeline.

# COMMAND ----------
def dq_check(df, key_cols, table_name):
    total = df.count()
    if total == 0:
        raise ValueError(f"{table_name}: 0 rows after Silver transform — aborting")
    nulls = df.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in key_cols]).first()
    max_null_rate = max((nulls[c] or 0) / total for c in key_cols)
    print(f"{table_name}: {total} rows, max null-rate on key cols = {max_null_rate:.2%}")
    if max_null_rate > 0.05:
        raise ValueError(f"{table_name} failed DQ gate: {max_null_rate:.2%} nulls on key columns")

dq_check(co2_silver, ["country_code", "year", "co2_emissions_mt"], "silver_co2_energy")
dq_check(risk_silver, ["country_code", "region", "composite_climate_risk_score"], "silver_regional_climate_risk")
dq_check(company_silver, ["company_id", "country_code"], "silver_company_esg")
print("All Silver tables passed the data quality gate.")

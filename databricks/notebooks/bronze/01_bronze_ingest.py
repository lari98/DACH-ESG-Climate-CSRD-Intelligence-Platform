# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze — Raw Ingestion
# MAGIC Lands raw CO2/energy, regional climate risk, and company ESG files as Delta tables with
# MAGIC audit columns. No transformation beyond adding lineage metadata. Source: files produced by
# MAGIC `python/app/ingestion` and landed in the `raw` Azure Blob container (mounted below), or the
# MAGIC bundled `data/sample` files when running in `sample` data mode.

# COMMAND ----------
from pyspark.sql import functions as F

dbutils.widgets.text("data_mode", "sample", "Data mode: sample|live")
dbutils.widgets.text("raw_path", "/mnt/dach-esg/raw", "Raw landing path")

DATA_MODE = dbutils.widgets.get("data_mode")
RAW_PATH = dbutils.widgets.get("raw_path")

BRONZE_DB = "dach_esg_bronze"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {BRONZE_DB}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Load each raw dataset and write to Bronze Delta with lineage columns

# COMMAND ----------
SOURCE_FILES = {
    "co2_energy": "sample_co2_energy_dach.csv",
    "regional_climate_risk": "sample_regional_climate_risk.csv",
    "company_esg": "sample_company_esg.csv",
}

for table, filename in SOURCE_FILES.items():
    path = f"{RAW_PATH}/{filename}"
    df = (
        spark.read.option("header", True).option("inferSchema", True).csv(path)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.lit(filename))
        .withColumn("_data_mode", F.lit(DATA_MODE))
    )
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{BRONZE_DB}.bronze_{table}")
    )
    print(f"Bronze table {BRONZE_DB}.bronze_{table}: {df.count()} rows")

# COMMAND ----------
# MAGIC %md
# MAGIC Bronze tables are append-friendly, immutable-by-convention landing tables. Silver notebook
# MAGIC handles all cleaning, typing, and deduplication.

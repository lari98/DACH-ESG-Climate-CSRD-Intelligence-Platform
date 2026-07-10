# Databricks notebook source
# MAGIC %md
# MAGIC # Gold — Business KPI Tables
# MAGIC Builds the business-facing KPI tables consumed by the API/dashboard: emissions trends,
# MAGIC energy mix, ESG/CSRD readiness, climate risk, and Scope 1/2/3 rollups.

# COMMAND ----------
from pyspark.sql import functions as F

SILVER_DB = "dach_esg_silver"
GOLD_DB = "dach_esg_gold"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {GOLD_DB}")

# COMMAND ----------
# MAGIC %md ## gold_co2_emissions + gold_energy_mix

# COMMAND ----------
co2 = spark.table(f"{SILVER_DB}.silver_co2_energy")

gold_co2 = co2.select(
    "country_code", "year", "co2_emissions_mt", "co2_per_capita_t", "data_quality"
).withColumn("_updated_at", F.current_timestamp())

gold_energy_mix = co2.select(
    "country_code", "year", "renewable_share_pct", "fossil_share_pct", "nuclear_share_pct",
    "electricity_generation_twh", "electricity_price_eur_mwh", "data_quality"
).withColumn("_updated_at", F.current_timestamp())

gold_co2.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_co2_emissions")
gold_energy_mix.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_energy_mix")

# COMMAND ----------
# MAGIC %md ## gold_climate_risk

# COMMAND ----------
risk = spark.table(f"{SILVER_DB}.silver_regional_climate_risk")
gold_risk = risk.withColumn("_updated_at", F.current_timestamp())
gold_risk.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_climate_risk")

# COMMAND ----------
# MAGIC %md ## gold_esg_scores + gold_scope_emissions

# COMMAND ----------
company = spark.table(f"{SILVER_DB}.silver_company_esg")

gold_esg = company.select(
    "company_id", "company_name", "country_code", "sector",
    "esg_readiness_score", "csrd_readiness_score", "reporting_gaps_count", "data_quality"
).withColumn("_updated_at", F.current_timestamp())

gold_scope = company.select(
    "company_id", "company_name", "country_code", "sector",
    "scope1_tco2e", "scope2_tco2e", "scope3_tco2e",
    (F.col("scope1_tco2e") + F.col("scope2_tco2e") + F.col("scope3_tco2e")).alias("total_tco2e"),
).withColumn("_updated_at", F.current_timestamp())

gold_esg.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_esg_scores")
gold_scope.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_scope_emissions")

# COMMAND ----------
# MAGIC %md ## gold_country_summary — one-row-per-country executive rollup

# COMMAND ----------
latest_year = gold_co2.agg(F.max("year")).first()[0]

country_summary = (
    gold_co2.filter(F.col("year") == latest_year).alias("c")
    .join(gold_energy_mix.filter(F.col("year") == latest_year).alias("e"), ["country_code", "year"])
    .join(
        gold_risk.groupBy("country_code").agg(F.avg("composite_climate_risk_score").alias("avg_climate_risk")),
        "country_code",
    )
    .join(
        gold_esg.groupBy("country_code").agg(
            F.avg("esg_readiness_score").alias("avg_esg_readiness"),
            F.avg("csrd_readiness_score").alias("avg_csrd_readiness"),
        ),
        "country_code",
    )
    .select(
        "country_code", "year", "co2_emissions_mt", "co2_per_capita_t",
        "renewable_share_pct", "avg_climate_risk", "avg_esg_readiness", "avg_csrd_readiness",
    )
    .withColumn("_updated_at", F.current_timestamp())
)

country_summary.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{GOLD_DB}.gold_country_summary")

display(country_summary)

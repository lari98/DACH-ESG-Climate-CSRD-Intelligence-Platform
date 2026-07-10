# Phase 3 — Data Sources, Schema & Data Dictionary

## Data Sources (free / public — production targets)

| Source | Data | Access |
|---|---|---|
| Our World in Data (`owid/co2-data`, `owid/energy-data`) | CO2 emissions, energy mix, per-capita figures, historical back to 1850s | Public CSV on GitHub, no key required |
| Eurostat | Energy balances, greenhouse gas inventories, regional (NUTS2) statistics for DE/AT | REST API (`ec.europa.eu/eurostat/api`), no key required |
| DESTATIS (Germany) | National emissions & energy statistics | Public API / CSV downloads |
| Statistik Austria | Austrian energy & emissions statistics | Public downloads |
| Swiss Federal Statistical Office (BFS) / BFE | Swiss energy & climate statistics | Public downloads |
| Copernicus / EEA climate indicators | Climate risk indicators (temperature, precipitation anomalies) | Public API |
| Company ESG sample data | User-entered via dashboard "Company ESG Input" tab | Generated locally, not scraped |

> **Sandbox note:** this build environment has no outbound access to the above hosts, so the
> repository ships with a generated, clearly-labeled **sample** dataset (`data/sample/`,
> `data_quality = "sample"`) so every layer of the platform (ingestion → Lakehouse → dashboard) is
> runnable end-to-end today. `python/app/ingestion/` is already wired to pull the real sources — set
> `DATA_MODE=live` once network/API access is available and it will populate `data/raw/` instead.

## Folder Structure

```
data/
├── raw/        # immutable landing zone — exact files as ingested (Bronze source)
├── cleaned/    # validated + standardized output of the cleaning/validation layer (Silver-equivalent, local mode)
└── sample/     # offline demo dataset, always tagged data_quality = "sample"
```

## Database Schema (Gold / serving layer)

### `co2_energy` (per country, per year)
| Column | Type | Description |
|---|---|---|
| country_code | varchar(2) | ISO-3166 alpha-2 (DE, AT, CH) |
| country_name / country_name_de | varchar | English / German display name |
| year | int | Calendar year |
| co2_emissions_mt | float | Total CO2 emissions, megatonnes |
| co2_per_capita_t | float | CO2 emissions per capita, tonnes |
| renewable_share_pct | float | % of electricity generation from renewables |
| fossil_share_pct | float | % from fossil sources |
| nuclear_share_pct | float | % from nuclear |
| electricity_generation_twh | float | Total electricity generated, TWh |
| electricity_price_eur_mwh | float | Average wholesale electricity price, EUR/MWh |
| data_quality | varchar | `official` \| `estimated` \| `sample` |

### `regional_climate_risk` (per country, per region)
| Column | Type | Description |
|---|---|---|
| country_code | varchar(2) | DE / AT / CH |
| region | varchar | State / Bundesland / Kanton |
| physical_risk_score | float 0-10 | Physical climate risk (flood, heat, drought composite) |
| transition_risk_score | float 0-10 | Policy/market transition risk |
| flood_risk_score | float 0-10 | Flood-specific sub-score |
| heat_stress_score | float 0-10 | Heat-stress sub-score |
| composite_climate_risk_score | float 0-10 | Average of physical + transition |
| risk_level | varchar | Low / Medium / High |
| data_quality | varchar | official / estimated / sample |

### `company_esg` (per company, latest reporting period)
| Column | Type | Description |
|---|---|---|
| company_id | varchar | Internal ID |
| company_name | varchar | Display name |
| country_code | varchar(2) | Country of primary operations |
| sector | varchar | Industry sector |
| scope1_tco2e | float | Direct emissions, tCO2e |
| scope2_tco2e | float | Energy-indirect emissions, tCO2e |
| scope3_tco2e | float | Value-chain emissions, tCO2e |
| esg_readiness_score | float 0-100 | Composite ESG maturity score |
| csrd_readiness_score | float 0-100 | CSRD/ESRS audit-readiness score |
| reporting_gaps_count | int | Number of flagged disclosure gaps |
| data_quality | varchar | official / estimated / sample |

## Update Strategy

- **Cadence**: annual data (CO2/energy) refreshed quarterly; company ESG input refreshed on user
  submission (real-time); climate risk indicators refreshed monthly as new climate model runs land.
- **Mechanism (production)**: Azure Function on a timer trigger calls `python/app/ingestion` →
  writes to `raw` Blob container → Databricks workflow job runs Bronze→Silver→Gold on a schedule →
  Gold tables synced to Azure SQL → dashboard reads live.
- **Mechanism (local)**: `scripts/generate_sample_data.py` or `python -m app.ingestion.run_all`
  (real-source mode) regenerates `data/raw` and `data/cleaned` on demand.
- **Versioning**: Delta Lake time travel on Bronze/Silver/Gold gives point-in-time auditability,
  required for CSRD-style audit trails.
- **Validation gate**: no data is promoted Bronze→Silver→Gold unless it passes the checks in
  `python/app/validation` (row-count thresholds, null-rate thresholds, referential integrity of
  country/region codes, numeric range checks).

# Phase 1 — Business Scope

## Project
**DACH ESG, Climate Risk & CSRD Intelligence Platform**

## Why This Matters in the DACH Region

Germany, Austria, and Switzerland sit at the center of Europe's sustainability-regulation wave. The EU
Corporate Sustainability Reporting Directive (CSRD) now requires thousands of German and Austrian
companies (and Swiss companies with EU exposure) to report detailed, audited ESG data — Scope 1/2/3
emissions, climate risk exposure, energy transition progress, and forward-looking transition plans —
starting in phased waves through 2028. At the same time:

- **Germany** is mid-*Energiewende*, with an accelerating renewables build-out and a coal phase-out
  target, creating constant year-over-year shifts in energy mix and grid carbon intensity.
- **Austria** has one of the highest renewable electricity shares in Europe (large hydro base) but
  faces climate risk concentrated in Alpine regions (flooding, glacier retreat, heat stress).
- **Switzerland** is not an EU member but aligns closely with CSRD-equivalent reporting (Swiss Code of
  Obligations non-financial reporting duty) and has some of the strictest banking/insurance ESG
  disclosure expectations in the world (FINMA, SIX Exchange).

Companies, banks, insurers, and consultancies across DACH need a single place to see: where emissions
and energy data stand today, where they are heading, how exposed a region or company is to climate
risk, and how ready an organization is for CSRD audit — in both English and German, to the standard
regulators and Big Four auditors expect.

## Target Users

- **ESG / Sustainability Managers** — track KPIs, benchmark against peers and national baselines.
- **Internal & External Auditors** — verify data lineage, drill into source figures, export audit trails.
- **Management Consultants (Deloitte, KPMG, PwC, EY, Big Four/Big Three style engagements)** — build
  client-ready ESG and climate-risk narratives quickly.
- **CFO / Finance Teams** — connect ESG readiness and climate risk to financial and reporting exposure.
- **Banks & Insurers (UBS, Swiss Re, Munich Re, Allianz style users)** — assess climate risk exposure
  in loan books, underwriting portfolios, and investment portfolios by region/sector.
- **Energy Companies & Utilities** — monitor generation mix, renewable share, and emission intensity
  trends across DACH.
- **Data / Analytics / Platform Teams** — reference implementation of a modern lakehouse + AI ESG
  stack.

## Business Problems Solved

1. **Fragmented data** — CO₂, energy, and climate data are scattered across Eurostat, national
   statistics offices, and internal spreadsheets. The platform centralizes this into one governed
   Lakehouse.
2. **Manual, slow ESG/CSRD reporting** — Excel-driven reporting is slow and error-prone. The platform
   automates ingestion → validation → KPI computation → export.
3. **No forward view** — Most ESG dashboards are backward-looking. This platform adds forecasting
   (1/3/5/10y, 2030/2040/2050 horizons) and scenario simulation for CO₂, renewables, electricity
   price, and climate risk.
4. **Weak climate-risk visibility** — Physical and transition climate risk is rarely visualized at
   region/canton/state granularity. The platform's advanced map system closes that gap.
5. **English-only tools in a German-speaking market** — Full EN/DE bilingual UI, labels, tooltips,
   AI insights, and exported reports.
6. **No AI-assisted interpretation** — An embedded ESG/CSRD assistant explains "what changed," "why
   it matters," and "what to do about it," in business language, not raw numbers.

## Core KPIs Tracked

| KPI | Description |
|---|---|
| CO₂ emissions (total & per capita) | National and regional emissions trend |
| Energy mix | Share of coal, gas, nuclear, hydro, wind, solar, other renewables |
| Renewable share (%) | Renewable electricity generation as % of total |
| Electricity generation & price | Generation volumes and market price trends |
| Scope 1 / Scope 2 / Scope 3 emissions | Company-level input and benchmarking |
| ESG readiness score | Composite maturity score (governance, data quality, disclosure coverage) |
| CSRD readiness score | Gauge of audit-readiness against CSRD/ESRS requirements |
| Climate risk score | Composite physical + transition risk index by region |
| Reporting gaps | Missing/incomplete disclosure areas flagged for remediation |

## Project Story (LinkedIn / GitHub / CV / Interviews)

> Built a full-stack **DACH ESG, Climate Risk & CSRD Intelligence Platform** — an end-to-end reference
> implementation spanning Python data engineering (FastAPI, pydantic, SQLAlchemy), a Databricks
> Lakehouse (Bronze/Silver/Gold Delta tables, PySpark, MLflow forecasting & anomaly detection), an
> Azure cloud architecture (Blob Storage, Azure SQL, Functions, Key Vault, Azure OpenAI, Monitor), and
> a consulting-grade bilingual (EN/DE) R Shiny dashboard with an advanced Leaflet climate-risk map,
> forecasting lab, and an embedded AI ESG/CSRD assistant. Modeled on the real reporting needs of
> Germany, Austria, and Switzerland under CSRD, the project demonstrates how a modern data + AI stack
> can turn fragmented public climate/energy data into audit-ready, forward-looking ESG intelligence —
> the kind of system used by consulting firms, banks, insurers, and energy companies across the DACH
> region.

**One-line pitch:** *"A production-grade ESG & climate-risk intelligence platform for the DACH market —
Python + Databricks + Azure + AI, wrapped in a bilingual, audit-ready Shiny dashboard."*

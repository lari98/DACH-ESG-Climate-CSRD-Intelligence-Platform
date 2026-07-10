# Data Freshness, Cost & Accuracy Policy

## Cost: 100% free, no hidden charges

Every data source wired into `python/app/ingestion/sources.py` is free and requires **no paid API
key**:

| Source | Cost | Auth |
|---|---|---|
| Our World in Data (CO2 + energy CSVs on GitHub) | Free, unlimited | None |
| Eurostat REST API | Free, unlimited | None |
| ENTSO-E Transparency Platform (near-real-time electricity generation/mix for DE/AT/CH) | Free | Free self-service token (no payment, no card) |
| DESTATIS / Statistik Austria / BFS public downloads | Free | None |

Nothing in this project calls a metered/paid API. Azure OpenAI (used only for the AI panels) is the
one component with a real cost if deployed to Azure — the platform is designed so it **runs fully
without it** via the local rule-based fallback in `python/app/ai` (see Phase 8 notes), so there is
never a forced paid dependency.

## "Real-time, 100% accurate" — an honest constraint

It's important to be precise here rather than overpromise:

- **National CO2 emissions and annual energy-mix statistics (Eurostat/OWID/DESTATIS) are not
  published hourly by anyone, free or paid.** These are official statistics compiled annually
  (sometimes quarterly), with a typical publication lag of several months. No data provider — free
  or commercial — offers verified, audited, hourly national CO2 emissions. Any tool claiming that is
  not using official/auditable figures. This platform pulls the freshest **official** figures
  available and timestamps every record so users always know exactly how current it is.
- **What genuinely can be near-real-time and free**: grid-level electricity generation and fuel mix
  from **ENTSO-E Transparency Platform**, updated every 15–60 minutes. The ingestion layer supports
  this as a live, high-frequency source for the "current generation mix" views, clearly distinguished
  from the annual/official emissions series.
- **Company ESG input data** (user-submitted) is genuinely real-time — it updates the instant a user
  submits the "Company ESG Input" form.

## What "hourly refresh" means in this project

- An **hourly scheduled job** (`scripts/hourly_refresh.py`, wired to a cron entry locally and to an
  Azure Function timer trigger in production — see `azure/functions/hourly_ingestion`) runs every
  hour and:
  1. Re-pulls whichever sources have new data available (ENTSO-E near-real-time feed every run;
     Eurostat/OWID/official annual series only when the source itself has actually published a new
     value — re-fetching hourly is harmless and free, it simply returns unchanged data most hours).
  2. Runs the **double-check reconciliation** step below before anything is promoted to the serving
     database.
  3. Logs a freshness timestamp (`last_checked_at`) and a "source published date" (`source_as_of`)
     separately, so the dashboard can honestly show *both* "we last checked an hour ago" and "the
     underlying statistic is as of Q2 2026" rather than implying the statistic itself is an hour old.

## Double-check / accuracy gate

Two independent checks run on every ingestion, implemented in
`python/app/validation/reconciliation.py`:

1. **Schema + range validation gate** (already in `validation/checks.py`): every row must pass
   pydantic type/range checks; a dataset is only promoted if ≥95% of rows pass.
2. **Cross-run consistency check** (new): each new pull is compared against the last successfully
   loaded snapshot. Any value that moves by more than a configurable tolerance (default: 15% for
   annual series, 40% for the more volatile hourly generation-mix series) is flagged as an anomaly,
   logged, and **excluded from promotion** until a human/AI reviews it — it does not silently
   overwrite good data with a bad pull (e.g. a truncated download or a source outage returning zeros).

This gives an honest, auditable "double-checked" pipeline: nothing reaches the dashboard without
passing both the shape/range gate and the anomaly-vs-history gate, and every record carries a visible
`data_quality` + `source_as_of` + `last_checked_at` trail.

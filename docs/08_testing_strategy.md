# Phase 10 — Testing Strategy

## Coverage map

| Test type | Location | Status |
|---|---|---|
| Python unit tests | `python/tests/test_cleaning.py`, `test_validation.py` | Automated, in CI |
| Data quality tests | `python/tests/test_validation.py`, `test_reconciliation.py` | Automated, in CI |
| Reconciliation / double-check tests | `python/tests/test_reconciliation.py` | Automated, in CI |
| API tests | `python/tests/test_api.py` | Automated, in CI |
| Database tests | `python/tests/test_db.py` (Phase 10) | Automated, in CI |
| LLM output tests | `python/tests/test_ai.py`, `test_ai_grounding.py`, `test_llm_output_quality.py` (Phase 10) | Automated, in CI (offline fallback path) |
| Security tests | `python/tests/test_security_and_gdpr.py` (Phase 10) | Automated, in CI |
| GDPR checks | `python/tests/test_security_and_gdpr.py` (Phase 10) | Automated, in CI |
| Runtime/performance tests | `python/tests/test_performance.py` (Phase 10) | Automated, in CI |
| R dashboard unit tests | `r_dashboard/tests/testthat/test-translations.R`, `test-forecast-helpers.R` (Phase 10) | Automated, `testthat` |
| R dashboard UI/app tests | `r_dashboard/tests/testthat/test-app-shinytest2.R` (Phase 10) | Skeleton — requires Chrome/`shinytest2`, skipped in headless CI until provisioned |
| Visualization tests | `docs/07_visualization_quality_review.md` checklist + shinytest2 skeleton | Manual checklist + partial automation |
| User acceptance tests | UAT checklist below | Manual |

## Running the suite

```bash
cd python
pip install -r requirements.txt
pytest -q                      # all Python tests (cleaning, validation, reconciliation,
                                #   API, AI/grounding, DB, security/GDPR, performance)
```

```r
# from r_dashboard/
install.packages("testthat")
Rscript tests/testthat.R
```

## Data quality tests (what they actually check)

`test_validation.py` and `test_reconciliation.py` together enforce the platform's two-gate data
quality policy described in `docs/04_data_freshness_and_accuracy.md`: (1) every row must satisfy
pydantic type/range constraints, with a dataset only promoted if ≥95% of rows pass; (2) every
new pull is reconciled against the last loaded snapshot and any value moving beyond tolerance is
withheld. `test_db.py` adds a roundtrip check (write → read back → values match) and confirms
the `company_id` uniqueness constraint actually rejects a duplicate insert.

## LLM output tests (what "testing an LLM" means here)

Since live Azure OpenAI calls aren't deterministic (and cost money), the automated suite tests
the **offline fallback path** for every AI function — this is the path CI and any zero-budget
deployment actually exercises. It checks: bilingual outputs differ between `en`/`de`, every
offline response self-identifies as `[Offline mode]`/`[Offline-Modus]` (so a user never mistakes
a canned response for a verified AI answer), structured outputs (e.g. `visual_insight_bundle`)
always contain all required keys, and the `check_grounding()` heuristic correctly flags a
fabricated number while accepting a matching one (`test_ai_grounding.py`). A recommended
follow-up once an Azure OpenAI key is available: a small "golden set" of ~20 question/context
pairs run against the live model with the same grounding check, tracked over time to catch
regressions from model/prompt changes.

## Security tests (what they cover, and what they don't)

`test_security_and_gdpr.py` is an automatable first line of defense, not a substitute for a real
review: it checks that no personal-data-shaped columns exist in the schema, that `/health`
never echoes a secret, that no real-looking secret is hardcoded as a config default, and that a
classic SQL-injection-style path parameter is handled safely by the ORM without a 500 error.
Before a production launch, add: a dependency vulnerability scan (`pip-audit` / `safety` for
Python, `renv::audit()` or GitHub's R advisory database for R), and tighten the CORS policy
(currently `allow_origins=["*"]` for local development — see the test that documents this
explicitly).

## GDPR checks

Beyond the automated schema check, GDPR compliance is primarily an architectural property (see
`docs/02_architecture.md` and `docs/05_ai_llm_design.md`): the platform holds no individual
personal data by design, secrets live in Key Vault/`.env` (never committed), and AI prompts never
include personal data. Manual GDPR review checklist before production: confirm the Azure OpenAI
resource region and data-processing agreement, confirm Company ESG Input form doesn't collect
any individual contact details beyond what's needed, and confirm log retention in Azure Monitor
has a defined deletion policy.

## User Acceptance Testing (UAT) checklist

Run through this manually before considering a release "done":

- [ ] EN/DE toggle changes every visible label, tooltip, chart title, and AI panel — no
      untranslated English text remains when DE is selected (and vice versa)
- [ ] Dark/light mode toggle is legible in both modes, including chart text and map controls
- [ ] Every Forecast Lab sub-tab (all 7) accepts a country change, horizon change, and scenario
      change, and the chart/AI panel/risk badge all update together
- [ ] Climate Risk Map: switching base-map style, layer, and view (past/present/future/next-
      future) all visibly change the map; clicking a marker populates the region detail + AI panel
- [ ] Company ESG Input: submitting a new company immediately appears in the benchmarking chart
      and the Scope 1/2/3 tab
- [ ] Report Export produces a downloadable file in both HTML and PDF format, in both languages
- [ ] All KPI cards, charts, and tables reflect the same underlying filtered dataset — no stale
      or contradictory numbers between panels on the same tab
- [ ] Mobile/tablet width (resize browser to ~768px): sidebar collapses, boxes stack, no
      horizontal scroll on the main content area
- [ ] AI Assistant tab: asking a question returns an answer (live or clearly-labeled offline
      fallback) within a few seconds, never a blank/broken panel

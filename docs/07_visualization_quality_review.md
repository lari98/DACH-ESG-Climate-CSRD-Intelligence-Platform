# Phase 9 — Visualization Quality Review

## Chart/visual inventory (already built, cross-referenced)

| Requirement | Where it lives |
|---|---|
| Interactive maps | `r_dashboard/app/modules/mod_climate_map.R` — Leaflet, layer control, style switcher, timeline |
| Drill-down filters | Every module's country/region/sector/metric filters + DT tables with `filter="top"` |
| Country comparison | `mod_country_comparison.R` — multi-line + radar |
| Time-series charts | `mod_executive_overview.R`, `mod_country_comparison.R`, `mod_energy_mix.R` |
| Forecast charts | `mod_forecasting_lab.R` — historical + forecast + 95% CI ribbon, all 7 predictors |
| Waterfall chart for Scope 1/2/3 | `mod_scope_emissions.R` — `plot_ly(type = "waterfall")` |
| KPI cards | `mod_executive_overview.R` — `valueBoxOutput` x4 |
| Risk heatmap | `mod_climate_map.R` — `addHeatmap()` layer + `mod_energy_mix.R` calendar heatmap |
| Executive dashboard | `mod_executive_overview.R` (KPIs + trend + AI panel + data quality scorecard) |
| Audit/reporting dashboard | `mod_report_export.R` — audit trail table + CSRD report export |

## Quality checklist

**Colors** — Enterprise DACH palette defined once in `global.R` (`THEME` list) and reused across
every chart and the CSS theme: deep forest green primary, muted gold accent, and a 3-tier
red/amber/green risk scale used consistently for risk levels, gauges, and map markers. No
chart uses more than the defined palette — avoids the "childish/over-colorful" failure mode
called out in the original spec.

**Layout** — `shinydashboard` box/column grid throughout; every tab follows the same pattern
(filters row → primary chart(s) → detail/AI panel → drill-down table), so users build a
predictable mental model moving between the 10 tabs.

**Responsiveness** — `shinydashboard`'s grid is responsive by default (Bootstrap 3 columns);
Phase 9 added explicit breakpoints in `custom.css` (`@media (max-width: 991px)` and `767px`) to
stack boxes and collapse the sidebar cleanly on tablet/mobile, plus overflow handling so
DT/Plotly/Leaflet outputs don't break the layout on narrow screens.

**Accessibility** — Phase 9 additions to `custom.css`: visible focus outlines on all interactive
elements (WCAG 2.4.7), a skip-link pattern, and darkened the sample-data badge text color to
meet WCAG AA contrast on a light background (also mirrored for dark mode). Remaining
recommended follow-up before a production launch: run an automated audit (e.g. `axe-core`
against the rendered app) and add `aria-label`s to icon-only buttons in the map toolbar
(reset/compare-regions buttons in `mod_climate_map.R`).

**Chart readability** — every chart has an explicit axis title (no bare Plotly defaults), value
labels/tooltips via Plotly hover, and consistent number formatting; forecast charts always pair
the point forecast with its confidence band rather than showing a bare line, so uncertainty is
visible rather than implied.

**Business storytelling** — each tab pairs a chart with a plain-language panel: Executive
Overview's "What changed?" AI panel, the Forecast Lab's "AI insight" + risk-level badge, and the
Climate Map's "AI risk explanation" popup all translate the chart into a business statement
rather than leaving the user to interpret raw numbers alone.

## Known limitations (honest, not glossed over)

- The climate risk map uses synthetic region centroids (see comment in `mod_climate_map.R`) since
  real NUTS2/Kanton shapefiles weren't available offline in this build environment — swap in `sf`
  polygons from Eurostat/BFS for production-grade choropleth boundaries instead of point markers.
- No automated visual-regression testing yet (e.g. `shinytest2` screenshot diffing) — see
  `docs/08_testing_strategy.md` (Phase 10) for the plan to add this.

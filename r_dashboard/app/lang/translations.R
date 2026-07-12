# Bilingual (EN/DE) label dictionary used throughout the dashboard.
# Usage: t("kpi_co2", lang())  -> returns the label in the active language.
# Every UI string, tooltip, chart title, and AI panel heading should route through this
# function so language toggling is instantaneous and complete (no partially-translated screens).

TRANSLATIONS <- list(
  # --- App shell ---
  app_title            = list(en = "DACH ESG, Climate Risk & CSRD Intelligence Platform",
                               de = "DACH ESG-, Klimarisiko- & CSRD-Intelligence-Plattform"),
  lang_toggle           = list(en = "DE", de = "EN"),  # button shows the OTHER language
  theme_toggle_dark     = list(en = "Dark mode", de = "Dunkelmodus"),
  theme_toggle_light    = list(en = "Light mode", de = "Hellmodus"),

  # --- Main tabs ---
  tab_overview          = list(en = "Executive Overview", de = "Management-Übersicht"),
  tab_comparison        = list(en = "DACH Country Comparison", de = "DACH-Ländervergleich"),
  tab_map               = list(en = "Climate Risk Map", de = "Klimarisiko-Karte"),
  tab_esg_csrd          = list(en = "ESG & CSRD Readiness", de = "ESG- & CSRD-Bereitschaft"),
  tab_forecast_lab      = list(en = "Predictor & Forecasting Lab", de = "Prognose- & Vorhersagelabor"),
  tab_scope             = list(en = "Scope 1/2/3 Emissions Analysis", de = "Scope 1/2/3 Emissionsanalyse"),
  tab_energy_mix        = list(en = "Energy Mix & Renewables", de = "Energiemix & Erneuerbare"),
  tab_company_input     = list(en = "Company ESG Input & Benchmarking", de = "Unternehmens-ESG-Eingabe & Benchmarking"),
  tab_ai_assistant      = list(en = "AI ESG Assistant", de = "KI-ESG-Assistent"),
  tab_report_export     = list(en = "Report Export & Audit View", de = "Berichtsexport & Audit-Ansicht"),

  # --- Forecast Lab sub-tabs ---
  sub_co2_predictor     = list(en = "CO2 Emissions Predictor", de = "CO2-Emissionsprognose"),
  sub_renewable_pred    = list(en = "Renewable Energy Predictor", de = "Prognose erneuerbare Energien"),
  sub_price_predictor   = list(en = "Electricity Price Predictor", de = "Strompreisprognose"),
  sub_climate_risk_pred = list(en = "Climate Risk Predictor", de = "Klimarisikoprognose"),
  sub_esg_readiness_pred= list(en = "ESG Readiness Predictor", de = "ESG-Bereitschaftsprognose"),
  sub_scope_forecast    = list(en = "Scope 1/2/3 Forecast", de = "Scope 1/2/3-Prognose"),
  sub_scenario_sim      = list(en = "Scenario Simulator", de = "Szenariosimulator"),

  # --- Common controls ---
  filter_country        = list(en = "Country", de = "Land"),
  filter_region         = list(en = "Region / Canton / State", de = "Region / Kanton / Bundesland"),
  filter_horizon        = list(en = "Forecast horizon", de = "Prognosehorizont"),
  filter_timeline       = list(en = "Timeline", de = "Zeitachse"),
  filter_scenario       = list(en = "Scenario", de = "Szenario"),
  filter_metric         = list(en = "Metric", de = "Kennzahl"),
  filter_sector         = list(en = "Sector", de = "Sektor"),
  filter_risk_level     = list(en = "Risk level", de = "Risikostufe"),
  btn_export            = list(en = "Export", de = "Exportieren"),
  btn_reset_map         = list(en = "Reset map", de = "Karte zurücksetzen"),
  btn_play              = list(en = "Play", de = "Abspielen"),
  btn_pause             = list(en = "Pause", de = "Pause"),
  btn_compare_regions   = list(en = "Compare two regions", de = "Zwei Regionen vergleichen"),

  # --- KPIs ---
  kpi_co2               = list(en = "CO2 Emissions (Mt)", de = "CO2-Emissionen (Mt)"),
  kpi_co2_capita        = list(en = "CO2 per Capita (t)", de = "CO2 pro Kopf (t)"),
  kpi_renewable         = list(en = "Renewable Share (%)", de = "Anteil Erneuerbare (%)"),
  kpi_climate_risk      = list(en = "Climate Risk Score", de = "Klimarisiko-Score"),
  kpi_esg_readiness     = list(en = "ESG Readiness", de = "ESG-Bereitschaft"),
  kpi_csrd_readiness    = list(en = "CSRD Readiness", de = "CSRD-Bereitschaft"),
  kpi_reporting_gaps    = list(en = "Reporting Gaps", de = "Berichtslücken"),

  # --- AI panels ---
  ai_what_changed       = list(en = "What changed?", de = "Was hat sich geändert?"),
  ai_why_matters        = list(en = "Why it matters", de = "Warum es wichtig ist"),
  ai_risk_explanation   = list(en = "Risk explanation", de = "Risikoerklärung"),
  ai_business_impact    = list(en = "Business impact", de = "Geschäftliche Auswirkung"),
  ai_recommended_action = list(en = "Recommended action", de = "Empfohlene Maßnahme"),
  ai_csrd_implication   = list(en = "CSRD reporting implication", de = "CSRD-Berichtsimplikation"),
  ai_ask_placeholder    = list(en = "Ask the ESG assistant about DACH climate, energy, or CSRD readiness...",
                                de = "Fragen Sie den ESG-Assistenten zu DACH-Klima, Energie oder CSRD-Bereitschaft..."),

  data_sample_notice    = list(en = "Sample / demo data — not an official statistic",
                                de = "Beispiel-/Demodaten — keine offizielle Statistik"),
  data_live_notice      = list(en = "Live data from free public APIs (OWID / Eurostat)",
                                de = "Live-Daten aus freien öffentlichen APIs (OWID / Eurostat)"),

  # --- Executive Overview ---
  dq_scorecard_title    = list(en = "Data Quality Scorecard", de = "Datenqualitäts-Scorecard"),

  # --- Country Comparison ---
  chart_multiline_trend = list(en = "Multi-country trend", de = "Mehrländer-Trend"),
  chart_esg_radar       = list(en = "ESG Maturity Radar", de = "ESG-Reife-Radar"),
  table_drilldown_data  = list(en = "Drill-down data", de = "Detaildaten"),
  series_renewable_pct  = list(en = "Renewable %", de = "Erneuerbar %"),

  # --- Climate Risk Map ---
  panel_region_details       = list(en = "Region details", de = "Regionsdetails"),
  panel_ai_risk_explanation  = list(en = "AI risk explanation", de = "KI-Risikoerklärung"),
  map_style_light             = list(en = "Light (consulting)", de = "Hell (Consulting)"),
  map_style_standard          = list(en = "Standard", de = "Standard"),
  map_style_satellite         = list(en = "Satellite", de = "Satellit"),
  map_style_terrain           = list(en = "Terrain", de = "Gelände"),
  map_layer_composite         = list(en = "Composite risk (choropleth)", de = "Gesamtrisiko (Choroplethenkarte)"),
  map_layer_physical          = list(en = "Physical risk", de = "Physisches Risiko"),
  map_layer_transition        = list(en = "Transition risk", de = "Transitionsrisiko"),
  map_layer_flood             = list(en = "Flood risk", de = "Hochwasserrisiko"),
  map_layer_heat               = list(en = "Heat stress", de = "Hitzestress"),
  map_layer_heatmap           = list(en = "Emission intensity (heatmap)", de = "Emissionsintensität (Heatmap)"),
  map_layer_renewable         = list(en = "Renewable energy layer", de = "Erneuerbare-Energien-Layer"),
  map_view_present             = list(en = "Present", de = "Gegenwart"),
  map_view_past                = list(en = "Past (baseline)", de = "Vergangenheit (Basislinie)"),
  map_view_future              = list(en = "Future forecast", de = "Zukunftsprognose"),
  map_view_next_future         = list(en = "Next-future scenario", de = "Nahe-Zukunfts-Szenario"),
  map_region_click_hint        = list(en = "Click a marker to see region detail.",
                                       de = "Klicken Sie auf einen Marker, um Regionsdetails zu sehen."),

  # --- ESG & CSRD Readiness ---
  gauge_csrd_readiness  = list(en = "CSRD Readiness Gauge", de = "CSRD-Bereitschaftsanzeige"),
  gauge_esg_readiness   = list(en = "ESG Readiness Gauge", de = "ESG-Bereitschaftsanzeige"),
  table_company_benchmark = list(en = "Company benchmarking (drill-down)", de = "Unternehmensvergleich (Detailansicht)"),

  # --- Forecasting Lab ---
  panel_ai_insight          = list(en = "AI insight", de = "KI-Erkenntnis"),
  chart_scenario_comparison = list(en = "Scenario comparison", de = "Szenariovergleich"),
  series_historical_current = list(en = "Historical / Current", de = "Historisch / Aktuell"),
  series_forecast           = list(en = "Forecast", de = "Prognose"),
  series_ci95               = list(en = "95% CI", de = "95 %-Konfidenzintervall"),

  # --- Scope 1/2/3 Emissions ---
  chart_scope_stacked      = list(en = "Scope 1/2/3 by sector (stacked)", de = "Scope 1/2/3 nach Sektor (gestapelt)"),
  chart_emission_waterfall = list(en = "Emission composition (waterfall)", de = "Emissionszusammensetzung (Wasserfall)"),
  chart_emission_treemap   = list(en = "Emission category treemap", de = "Emissionskategorie-Treemap"),
  chart_sector_boxplot     = list(en = "Distribution by sector (box plot)", de = "Verteilung nach Sektor (Boxplot)"),
  series_total              = list(en = "Total", de = "Gesamt"),

  # --- Energy Mix ---
  chart_energy_area      = list(en = "Energy mix over time (stacked area)", de = "Energiemix im Zeitverlauf (gestapelte Fläche)"),
  chart_energy_sankey    = list(en = "Energy flow (Sankey)", de = "Energiefluss (Sankey)"),
  chart_renewable_heatmap= list(en = "Renewable share — calendar heatmap (by year/quarter, illustrative)",
                                 de = "Anteil Erneuerbare — Kalender-Heatmap (nach Jahr/Quartal, illustrativ)"),
  series_renewable        = list(en = "Renewable", de = "Erneuerbar"),
  series_fossil           = list(en = "Fossil", de = "Fossil"),
  series_nuclear          = list(en = "Nuclear", de = "Kernenergie"),
  series_grid             = list(en = "Grid", de = "Netz"),

  # --- Company ESG Input ---
  panel_add_company        = list(en = "Add / update company", de = "Unternehmen hinzufügen/aktualisieren"),
  lbl_company_name         = list(en = "Company name", de = "Unternehmensname"),
  lbl_scope1                = list(en = "Scope 1 (tCO2e)", de = "Scope 1 (tCO2e)"),
  lbl_scope2                = list(en = "Scope 2 (tCO2e)", de = "Scope 2 (tCO2e)"),
  lbl_scope3                = list(en = "Scope 3 (tCO2e)", de = "Scope 3 (tCO2e)"),
  lbl_esg_readiness_score  = list(en = "ESG readiness score", de = "ESG-Bereitschaftswert"),
  lbl_csrd_readiness_score = list(en = "CSRD readiness score", de = "CSRD-Bereitschaftswert"),
  btn_submit                = list(en = "Submit", de = "Absenden"),
  panel_peer_benchmark      = list(en = "Peer benchmarking", de = "Vergleich mit Wettbewerbern"),
  table_all_companies       = list(en = "All companies", de = "Alle Unternehmen"),
  notif_company_submitted   = list(en = "Company submitted.", de = "Unternehmen übermittelt."),
  series_esg_by_sector      = list(en = "ESG readiness by sector", de = "ESG-Bereitschaft nach Sektor"),

  # --- AI Assistant ---
  panel_ask_assistant     = list(en = "Ask the ESG / CSRD assistant", de = "ESG-/CSRD-Assistent fragen"),
  btn_ask                  = list(en = "Ask", de = "Fragen"),
  panel_csrd_assistant     = list(en = "CSRD readiness assistant", de = "CSRD-Bereitschaftsassistent"),
  lbl_company               = list(en = "Company", de = "Unternehmen"),
  panel_anomaly_explanation= list(en = "Anomaly explanation", de = "Anomalieerklärung"),

  # --- Report Export & Audit ---
  panel_export_report     = list(en = "Export CSRD-readiness report", de = "CSRD-Bereitschaftsbericht exportieren"),
  lbl_format                = list(en = "Format", de = "Format"),
  panel_audit_trail        = list(en = "Audit trail (data lineage)", de = "Audit-Trail (Datenherkunft)"),
  panel_export_raw          = list(en = "Export raw data", de = "Rohdaten exportieren"),
  btn_download_co2          = list(en = "CO2 & Energy (CSV)", de = "CO2 & Energie (CSV)"),
  btn_download_risk         = list(en = "Climate Risk (CSV)", de = "Klimarisiko (CSV)"),
  btn_download_companies    = list(en = "Company ESG (CSV)", de = "Unternehmens-ESG (CSV)")
)

t <- function(key, lang = "en") {
  entry <- TRANSLATIONS[[key]]
  if (is.null(entry)) return(key)
  val <- entry[[lang]]
  if (is.null(val)) entry[["en"]] else val
}

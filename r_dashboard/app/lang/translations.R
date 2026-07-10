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
                                de = "Live-Daten aus freien öffentlichen APIs (OWID / Eurostat)")
)

t <- function(key, lang = "en") {
  entry <- TRANSLATIONS[[key]]
  if (is.null(entry)) return(key)
  val <- entry[[lang]]
  if (is.null(val)) entry[["en"]] else val
}

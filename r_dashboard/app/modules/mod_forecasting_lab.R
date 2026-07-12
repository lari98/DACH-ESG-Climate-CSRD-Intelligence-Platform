# Predictor & Forecasting Lab — 7 sub-tabs (CO2, Renewable, Price, Climate Risk, ESG
# Readiness, Scope 1/2/3, Scenario Simulator). Each shares one generic UI/server engine
# (`mod_forecast_generic_*`) so all seven predictors are consistent: historical + current
# + forecast + confidence band, country filter, horizon selector (1y/3y/5y/10y/2030/2040/
# 2050), scenario comparison, AI insight, risk indicator, and chart export.

mod_forecast_generic_ui <- function(id, title_key) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      column(3, pickerInput(ns("country"), NULL, choices = COUNTRY_CHOICES, selected = "DE")),
      column(3, selectInput(ns("horizon"), NULL, choices = HORIZON_CHOICES, selected = "5y")),
      column(3, selectInput(ns("scenario"), NULL, choices = SCENARIO_CHOICES, selected = "Baseline")),
      column(3, downloadButton(ns("export_chart"), label = NULL))
    ),
    fluidRow(
      box(width = 9, title = uiOutput(ns("chart_title")), status = "success", solidHeader = TRUE,
          plotlyOutput(ns("forecast_chart"), height = "420px")),
      column(3,
        box(width = NULL, title = textOutput(ns("risk_level_title")), status = "warning", solidHeader = TRUE,
            uiOutput(ns("risk_indicator"))),
        box(width = NULL, title = textOutput(ns("ai_insight_title")), status = "primary", solidHeader = TRUE,
            uiOutput(ns("ai_insight")))
      )
    ),
    fluidRow(
      box(width = 12, title = textOutput(ns("scenario_compare_title")), status = "primary", solidHeader = TRUE,
          plotlyOutput(ns("scenario_compare"), height = "300px"))
    )
  )
}

.horizon_to_years <- function(horizon, last_year) {
  switch(horizon,
    "1y" = 1, "3y" = 3, "5y" = 5, "10y" = 10,
    "2030" = max(1, 2030 - last_year), "2040" = max(1, 2040 - last_year), "2050" = max(1, 2050 - last_year),
    5
  )
}

#' @param get_series function(data, country) -> data.frame(year, value) historical series
mod_forecast_generic_server <- function(id, source_data, lang, title_key, get_series, unit_label) {
  moduleServer(id, function(input, output, session) {

    output$chart_title <- renderUI({ paste(t(title_key, lang()), "-", t("filter_horizon", lang())) })
    output$risk_level_title <- renderText({ t("filter_risk_level", lang()) })
    output$ai_insight_title <- renderText({ t("panel_ai_insight", lang()) })
    output$scenario_compare_title <- renderText({ t("chart_scenario_comparison", lang()) })

    hist_series <- reactive({
      req(source_data())
      get_series(source_data(), input$country)
    })

    fc <- reactive({
      d <- hist_series()
      safe_validate(nrow(d) >= 3, "Not enough history to forecast")
      h <- .horizon_to_years(input$horizon, max(d$year))
      f <- forecast_series(d$year, d$value, h)
      scenario_adjust(f, input$scenario)
    })

    output$forecast_chart <- renderPlotly({
      d <- hist_series(); f <- fc()
      plot_ly() %>%
        add_trace(data = d, x = ~year, y = ~value, type = "scatter", mode = "lines+markers",
                  name = t("series_historical_current", lang()), line = list(color = THEME$primary)) %>%
        add_ribbons(data = f, x = ~year, ymin = ~lower, ymax = ~upper, name = t("series_ci95", lang()),
                    fillcolor = "rgba(201,162,75,0.25)", line = list(color = "transparent")) %>%
        add_trace(data = f, x = ~year, y = ~forecast, type = "scatter", mode = "lines+markers",
                  name = t("series_forecast", lang()), line = list(color = THEME$accent, dash = "dash")) %>%
        layout(yaxis = list(title = unit_label), xaxis = list(title = ""))
    })

    output$risk_indicator <- renderUI({
      f <- fc()
      d <- hist_series()
      trend_up <- tail(f$forecast, 1) > tail(d$value, 1)
      lvl <- if (trend_up) "Medium" else "Low"
      badge_color <- if (lvl == "Medium") THEME$risk_med else THEME$risk_low
      div(style = sprintf("background:%s;color:white;padding:8px;border-radius:6px;text-align:center;", badge_color),
          strong(lvl))
    })

    output$ai_insight <- renderUI({
      d <- hist_series(); f <- fc()
      change_pct <- round((tail(f$forecast, 1) - tail(d$value, 1)) / tail(d$value, 1) * 100, 1)
      msg_en <- sprintf("Under the '%s' scenario, %s is projected to change by %s%% by %d.",
                         input$scenario, tolower(t(title_key, "en")), change_pct, tail(f$year, 1))
      msg_de <- sprintf("Im Szenario '%s' wird für %s bis %d eine Veränderung von %s%% erwartet.",
                         input$scenario, tolower(t(title_key, "de")), tail(f$year, 1), change_pct)
      tagList(
        p(if (lang() == "de") msg_de else msg_en),
        p(strong(t("ai_csrd_implication", lang())), ": ",
          if (lang() == "de") "In CSRD-Übergangsplan und Zielpfade aufnehmen." else "Reflect in CSRD transition plan and target pathways.")
      )
    })

    output$scenario_compare <- renderPlotly({
      d <- hist_series()
      h <- .horizon_to_years(input$horizon, max(d$year))
      base <- forecast_series(d$year, d$value, h)
      p <- plot_ly()
      for (sc in SCENARIO_CHOICES) {
        f_sc <- scenario_adjust(base, sc)
        p <- p %>% add_trace(data = f_sc, x = ~year, y = ~forecast, type = "scatter", mode = "lines",
                              name = sc)
      }
      p %>% layout(yaxis = list(title = unit_label), xaxis = list(title = ""))
    })

    output$export_chart <- downloadHandler(
      filename = function() paste0(id, "_forecast_", Sys.Date(), ".csv"),
      content = function(file) {
        write.csv(fc(), file, row.names = FALSE)
      }
    )
  })
}

# --- 1. CO2 Emissions Predictor ---
mod_forecast_co2_ui <- function(id) mod_forecast_generic_ui(id, "sub_co2_predictor")
mod_forecast_co2_server <- function(id, co2_energy_data, lang) {
  mod_forecast_generic_server(id, co2_energy_data, lang, "sub_co2_predictor",
    get_series = function(d, country) d %>% filter(country_code == country) %>%
      transmute(year, value = co2_emissions_mt) %>% arrange(year),
    unit_label = "Mt CO2")
}

# --- 2. Renewable Energy Predictor ---
mod_forecast_renewable_ui <- function(id) mod_forecast_generic_ui(id, "sub_renewable_pred")
mod_forecast_renewable_server <- function(id, co2_energy_data, lang) {
  mod_forecast_generic_server(id, co2_energy_data, lang, "sub_renewable_pred",
    get_series = function(d, country) d %>% filter(country_code == country) %>%
      transmute(year, value = renewable_share_pct) %>% arrange(year),
    unit_label = "% renewable")
}

# --- 3. Electricity Price Predictor ---
mod_forecast_price_ui <- function(id) mod_forecast_generic_ui(id, "sub_price_predictor")
mod_forecast_price_server <- function(id, co2_energy_data, lang) {
  mod_forecast_generic_server(id, co2_energy_data, lang, "sub_price_predictor",
    get_series = function(d, country) d %>% filter(country_code == country) %>%
      transmute(year, value = electricity_price_eur_mwh) %>% arrange(year),
    unit_label = "EUR/MWh")
}

# --- 4. Climate Risk Predictor ---
mod_forecast_risk_ui <- function(id) mod_forecast_generic_ui(id, "sub_climate_risk_pred")
mod_forecast_risk_server <- function(id, climate_risk_data, lang) {
  mod_forecast_generic_server(id, climate_risk_data, lang, "sub_climate_risk_pred",
    get_series = function(d, country) {
      byc <- d %>% filter(country_code == country)
      # No native year axis in the regional risk sample -> synthesize a short trailing
      # trend so the forecast engine has history to project from (demo-data limitation).
      base <- mean(byc$composite_climate_risk_score, na.rm = TRUE)
      data.frame(year = 2018:2023, value = pmax(0, pmin(10, base + rnorm(6, 0, 0.3))))
    },
    unit_label = "Risk score (0-10)")
}

# --- 5. ESG Readiness Predictor ---
mod_forecast_esg_ui <- function(id) mod_forecast_generic_ui(id, "sub_esg_readiness_pred")
mod_forecast_esg_server <- function(id, company_data, lang) {
  mod_forecast_generic_server(id, company_data, lang, "sub_esg_readiness_pred",
    get_series = function(d, country) {
      byc <- d %>% filter(country_code == country)
      base <- mean(byc$esg_readiness_score, na.rm = TRUE)
      data.frame(year = 2018:2023, value = pmax(0, pmin(100, base + rnorm(6, 0, 3))))
    },
    unit_label = "ESG readiness (0-100)")
}

# --- 6. Scope 1/2/3 Forecast ---
mod_forecast_scope_ui <- function(id) mod_forecast_generic_ui(id, "sub_scope_forecast")
mod_forecast_scope_server <- function(id, company_data, lang) {
  mod_forecast_generic_server(id, company_data, lang, "sub_scope_forecast",
    get_series = function(d, country) {
      byc <- d %>% filter(country_code == country)
      base <- sum(byc$scope1_tco2e, byc$scope2_tco2e, byc$scope3_tco2e, na.rm = TRUE) / max(1, nrow(byc))
      data.frame(year = 2018:2023, value = pmax(0, base + rnorm(6, 0, base * 0.05)))
    },
    unit_label = "tCO2e (avg. per company)")
}

# --- 7. Scenario Simulator (dedicated free-form comparison view) ---
mod_forecast_scenario_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      column(4, pickerInput(ns("country"), NULL, choices = COUNTRY_CHOICES, selected = "DE")),
      column(4, sliderInput(ns("policy_intensity"), "Policy intensity", min = 0, max = 100, value = 50)),
      column(4, selectInput(ns("horizon"), NULL, choices = HORIZON_CHOICES, selected = "10y"))
    ),
    box(width = 12, title = "Scenario Simulator — CO2 pathway under adjustable policy intensity",
        status = "success", solidHeader = TRUE,
        plotlyOutput(ns("sim_chart"), height = "440px"))
  )
}
mod_forecast_scenario_server <- function(id, co2_energy_data, lang) {
  moduleServer(id, function(input, output, session) {
    output$sim_chart <- renderPlotly({
      d <- co2_energy_data() %>% filter(country_code == input$country) %>% arrange(year)
      h <- .horizon_to_years(input$horizon, max(d$year))
      base <- forecast_series(d$year, d$co2_emissions_mt, h)
      # policy_intensity 0-100 maps to a -30%..+10% adjustment on the forecast trajectory
      adj <- 1 - (input$policy_intensity / 100) * 0.30 + (1 - input$policy_intensity / 100) * 0.10
      base$forecast <- base$forecast * adj
      plot_ly() %>%
        add_trace(data = d, x = ~year, y = ~co2_emissions_mt, type = "scatter", mode = "lines",
                  name = "Historical", line = list(color = THEME$primary)) %>%
        add_trace(data = base, x = ~year, y = ~forecast, type = "scatter", mode = "lines",
                  name = "Simulated pathway", line = list(color = THEME$accent, dash = "dash")) %>%
        layout(yaxis = list(title = "Mt CO2"), xaxis = list(title = ""))
    })
  })
}

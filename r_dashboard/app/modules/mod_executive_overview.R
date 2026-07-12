# Module 1: Executive Overview — KPI cards + trend + AI "what changed" summary.

mod_executive_overview_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      column(3, pickerInput(ns("country"), NULL, choices = COUNTRY_CHOICES, selected = "DE")),
      column(9, div(class = "sample-data-badge", textOutput(ns("data_badge"))))
    ),
    fluidRow(
      valueBoxOutput(ns("kpi_co2"), width = 3),
      valueBoxOutput(ns("kpi_renewable"), width = 3),
      valueBoxOutput(ns("kpi_risk"), width = 3),
      valueBoxOutput(ns("kpi_csrd"), width = 3)
    ),
    fluidRow(
      box(width = 8, title = textOutput(ns("trend_title")), status = "success", solidHeader = TRUE,
          plotlyOutput(ns("trend_chart"), height = "360px")),
      box(width = 4, title = textOutput(ns("ai_title")), status = "success", solidHeader = TRUE,
          uiOutput(ns("ai_panel")))
    ),
    fluidRow(
      box(width = 12, title = textOutput(ns("dq_title")), status = "warning", solidHeader = TRUE,
          DTOutput(ns("dq_table")))
    )
  )
}

mod_executive_overview_server <- function(id, co2_energy_data, climate_risk_data, company_data, lang) {
  moduleServer(id, function(input, output, session) {

    # Reflect the *actual* data_quality of what was loaded (API "official"/"estimated"
    # vs. local-fallback "sample"), instead of always showing the sample-data notice.
    output$data_badge <- renderText({
      d <- co2_energy_data()
      is_sample <- !("data_quality" %in% names(d)) || any(d$data_quality == "sample", na.rm = TRUE)
      if (is_sample) t("data_sample_notice", lang()) else t("data_live_notice", lang())
    })
    output$trend_title <- renderText({ paste(t("kpi_co2", lang()), "-", t("filter_timeline", lang())) })
    output$ai_title <- renderText({ t("ai_what_changed", lang()) })
    output$dq_title <- renderText({ t("dq_scorecard_title", lang()) })

    filtered_co2 <- reactive({
      req(co2_energy_data())
      co2_energy_data() %>% filter(country_code == input$country)
    })

    output$kpi_co2 <- renderValueBox({
      d <- filtered_co2()
      latest <- d %>% filter(year == max(year))
      valueBox(round(latest$co2_emissions_mt, 1), t("kpi_co2", lang()), icon = icon("smog"), color = "green")
    })
    output$kpi_renewable <- renderValueBox({
      d <- filtered_co2()
      latest <- d %>% filter(year == max(year))
      valueBox(paste0(round(latest$renewable_share_pct, 1), "%"), t("kpi_renewable", lang()),
                icon = icon("leaf"), color = "olive")
    })
    output$kpi_risk <- renderValueBox({
      d <- climate_risk_data() %>% filter(country_code == input$country)
      avg_risk <- round(mean(d$composite_climate_risk_score, na.rm = TRUE), 1)
      valueBox(avg_risk, t("kpi_climate_risk", lang()), icon = icon("triangle-exclamation"),
                color = if (avg_risk > 7) "red" else if (avg_risk > 4) "yellow" else "green")
    })
    output$kpi_csrd <- renderValueBox({
      d <- company_data() %>% filter(country_code == input$country)
      avg_csrd <- if (nrow(d) > 0) round(mean(d$csrd_readiness_score, na.rm = TRUE), 1) else NA
      valueBox(ifelse(is.na(avg_csrd), "N/A", paste0(avg_csrd, "%")), t("kpi_csrd_readiness", lang()),
                icon = icon("clipboard-check"), color = "teal")
    })

    output$trend_chart <- renderPlotly({
      d <- filtered_co2()
      plot_ly(d, x = ~year, y = ~co2_emissions_mt, type = "scatter", mode = "lines+markers",
              line = list(color = THEME$primary, width = 3),
              marker = list(color = THEME$accent)) %>%
        layout(yaxis = list(title = t("kpi_co2", lang())), xaxis = list(title = ""),
               plot_bgcolor = "rgba(0,0,0,0)", paper_bgcolor = "rgba(0,0,0,0)")
    })

    output$ai_panel <- renderUI({
      d <- filtered_co2() %>% arrange(year)
      if (nrow(d) < 2) return(NULL)
      delta <- tail(d$co2_emissions_mt, 1) - d$co2_emissions_mt[nrow(d) - 1]
      direction <- if (delta < 0) (if (lang() == "de") "gesunken" else "decreased") else (if (lang() == "de") "gestiegen" else "increased")
      msg <- if (lang() == "de") {
        sprintf("CO2-Emissionen sind im letzten verfügbaren Jahr um %.1f Mt %s.", abs(delta), direction)
      } else {
        sprintf("CO2 emissions %s by %.1f Mt in the most recent available year.", direction, abs(delta))
      }
      tagList(
        p(strong(t("ai_what_changed", lang())), ": ", msg),
        p(strong(t("ai_recommended_action", lang())), ": ",
          if (lang() == "de") "Fortschritt im Vergleich zu Sektorbenchmarks prüfen." else "Review progress against sector benchmarks.")
      )
    })

    output$dq_table <- renderDT({
      d <- co2_energy_data()
      summary_df <- d %>% group_by(country_code) %>%
        summarise(rows = n(), completeness = round(mean(!is.na(co2_emissions_mt)) * 100, 1),
                  latest_year = max(year), .groups = "drop")
      datatable(summary_df, options = list(dom = "t", pageLength = 5), rownames = FALSE)
    })
  })
}

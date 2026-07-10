# Module 4: ESG & CSRD Readiness — gauge charts, drill-down, reporting gap scorecard.

mod_esg_csrd_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      column(4, pickerInput(ns("country"), NULL, choices = c("All" = "ALL", COUNTRY_CHOICES), selected = "ALL")),
      column(4, pickerInput(ns("sector"), NULL, choices = "All", selected = "All"))
    ),
    fluidRow(
      box(width = 6, title = "CSRD Readiness Gauge", status = "success", solidHeader = TRUE,
          plotlyOutput(ns("csrd_gauge"), height = "300px")),
      box(width = 6, title = "ESG Readiness Gauge", status = "success", solidHeader = TRUE,
          plotlyOutput(ns("esg_gauge"), height = "300px"))
    ),
    fluidRow(
      box(width = 12, title = "Company benchmarking (drill-down)", status = "primary", solidHeader = TRUE,
          DTOutput(ns("table")))
    )
  )
}

mod_esg_csrd_server <- function(id, company_data, lang) {
  moduleServer(id, function(input, output, session) {

    observe({
      updatePickerInput(session, "sector", choices = c("All", sort(unique(company_data()$sector))))
    })

    filtered <- reactive({
      d <- company_data()
      if (input$country != "ALL") d <- d %>% filter(country_code == input$country)
      if (!is.null(input$sector) && input$sector != "All") d <- d %>% filter(sector == input$sector)
      d
    })

    gauge_plot <- function(value, title) {
      plot_ly(
        type = "indicator", mode = "gauge+number",
        value = value,
        title = list(text = title),
        gauge = list(axis = list(range = list(0, 100)),
                     bar = list(color = THEME$primary),
                     steps = list(list(range = c(0, 40), color = THEME$risk_high),
                                  list(range = c(40, 70), color = THEME$risk_med),
                                  list(range = c(70, 100), color = THEME$risk_low)))
      )
    }

    output$csrd_gauge <- renderPlotly({
      d <- filtered()
      gauge_plot(round(mean(d$csrd_readiness_score, na.rm = TRUE), 1), t("kpi_csrd_readiness", lang()))
    })
    output$esg_gauge <- renderPlotly({
      d <- filtered()
      gauge_plot(round(mean(d$esg_readiness_score, na.rm = TRUE), 1), t("kpi_esg_readiness", lang()))
    })

    output$table <- renderDT({
      datatable(filtered(), filter = "top", options = list(pageLength = 10))
    })
  })
}

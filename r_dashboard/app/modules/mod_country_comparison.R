# Module 2: DACH Country Comparison — multi-line + radar + drill-down table.

mod_country_comparison_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      column(4, pickerInput(ns("countries"), NULL, choices = COUNTRY_CHOICES,
                             selected = COUNTRY_CHOICES, multiple = TRUE)),
      column(4, sliderInput(ns("year_range"), NULL, min = 2000, max = 2023, value = c(2000, 2023), sep = "")),
      column(4, selectInput(ns("metric"), NULL,
                             choices = c("CO2 emissions (Mt)" = "co2_emissions_mt",
                                         "Renewable share (%)" = "renewable_share_pct",
                                         "Electricity price (EUR/MWh)" = "electricity_price_eur_mwh")))
    ),
    fluidRow(
      box(width = 8, title = textOutput(ns("multiline_title")), status = "success", solidHeader = TRUE,
          plotlyOutput(ns("multiline"), height = "380px")),
      box(width = 4, title = textOutput(ns("radar_title")), status = "success", solidHeader = TRUE,
          plotlyOutput(ns("radar"), height = "380px"))
    ),
    fluidRow(
      box(width = 12, title = textOutput(ns("table_title")), status = "primary", solidHeader = TRUE,
          DTOutput(ns("table")))
    )
  )
}

mod_country_comparison_server <- function(id, co2_energy_data, lang) {
  moduleServer(id, function(input, output, session) {

    output$multiline_title <- renderText({ t("chart_multiline_trend", lang()) })
    output$radar_title <- renderText({ t("chart_esg_radar", lang()) })
    output$table_title <- renderText({ t("table_drilldown_data", lang()) })

    filtered <- reactive({
      req(co2_energy_data())
      co2_energy_data() %>%
        filter(country_code %in% input$countries,
               year >= input$year_range[1], year <= input$year_range[2])
    })

    output$multiline <- renderPlotly({
      d <- filtered()
      safe_validate(nrow(d) > 0, "No data for current filter")
      plot_ly(d, x = ~year, y = ~get(input$metric), color = ~country_code, type = "scatter", mode = "lines+markers") %>%
        layout(yaxis = list(title = input$metric), xaxis = list(title = ""))
    })

    output$radar <- renderPlotly({
      d <- filtered() %>% filter(year == max(year))
      safe_validate(nrow(d) > 0, "No data")
      plot_ly(type = "scatterpolar", fill = "toself") %>%
        add_trace(r = d$renewable_share_pct, theta = d$country_code, name = t("series_renewable_pct", lang())) %>%
        layout(polar = list(radialaxis = list(visible = TRUE, range = c(0, 100))))
    })

    output$table <- renderDT({
      datatable(filtered(), filter = "top", options = list(pageLength = 10))
    })
  })
}

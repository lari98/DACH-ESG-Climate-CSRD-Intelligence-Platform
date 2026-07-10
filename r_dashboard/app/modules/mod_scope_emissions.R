# Module: Scope 1/2/3 Emissions Analysis — stacked bar, waterfall, treemap, box plot.

mod_scope_emissions_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(column(4, pickerInput(ns("country"), NULL, choices = c("All" = "ALL", COUNTRY_CHOICES), selected = "ALL"))),
    fluidRow(
      box(width = 6, title = "Scope 1/2/3 by sector (stacked)", status = "success", solidHeader = TRUE,
          plotlyOutput(ns("stacked"), height = "360px")),
      box(width = 6, title = "Emission composition (waterfall)", status = "success", solidHeader = TRUE,
          plotlyOutput(ns("waterfall"), height = "360px"))
    ),
    fluidRow(
      box(width = 6, title = "Emission category treemap", status = "primary", solidHeader = TRUE,
          plotlyOutput(ns("treemap"), height = "360px")),
      box(width = 6, title = "Distribution by sector (box plot)", status = "primary", solidHeader = TRUE,
          plotlyOutput(ns("boxplot"), height = "360px"))
    )
  )
}

mod_scope_emissions_server <- function(id, company_data, lang) {
  moduleServer(id, function(input, output, session) {

    filtered <- reactive({
      d <- company_data()
      if (input$country != "ALL") d <- d %>% filter(country_code == input$country)
      d
    })

    by_sector <- reactive({
      filtered() %>% group_by(sector) %>%
        summarise(Scope1 = sum(scope1_tco2e), Scope2 = sum(scope2_tco2e), Scope3 = sum(scope3_tco2e), .groups = "drop")
    })

    output$stacked <- renderPlotly({
      d <- by_sector()
      plot_ly(d, x = ~sector, y = ~Scope1, type = "bar", name = "Scope 1", marker = list(color = THEME$primary)) %>%
        add_trace(y = ~Scope2, name = "Scope 2", marker = list(color = THEME$secondary)) %>%
        add_trace(y = ~Scope3, name = "Scope 3", marker = list(color = THEME$accent)) %>%
        layout(barmode = "stack", yaxis = list(title = "tCO2e"))
    })

    output$waterfall <- renderPlotly({
      d <- filtered()
      totals <- c(sum(d$scope1_tco2e), sum(d$scope2_tco2e), sum(d$scope3_tco2e))
      plot_ly(
        type = "waterfall",
        x = c("Scope 1", "Scope 2", "Scope 3", "Total"),
        y = c(totals, sum(totals)),
        measure = c("relative", "relative", "relative", "total")
      ) %>% layout(yaxis = list(title = "tCO2e"))
    })

    output$treemap <- renderPlotly({
      d <- by_sector() %>% pivot_longer(cols = c(Scope1, Scope2, Scope3), names_to = "scope", values_to = "value")
      # Plotly treemaps require every value used in `parents` to also exist as its own
      # labeled node (with parent = ""). Without the sector-level root rows below, the
      # leaf-only version renders a blank chart (parents point to undefined nodes).
      sector_totals <- d %>% group_by(sector) %>% summarise(value = sum(value), .groups = "drop")
      plot_ly(
        type = "treemap",
        labels = c(sector_totals$sector, paste(d$sector, d$scope)),
        parents = c(rep("", nrow(sector_totals)), d$sector),
        values = c(sector_totals$value, d$value)
      )
    })

    output$boxplot <- renderPlotly({
      d <- filtered()
      plot_ly(d, x = ~sector, y = ~scope3_tco2e, type = "box", boxpoints = "outliers",
              marker = list(color = THEME$primary))
    })
  })
}

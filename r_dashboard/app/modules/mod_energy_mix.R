# Module: Energy Mix & Renewables — area chart, Sankey energy flow, calendar heatmap.

mod_energy_mix_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(column(4, pickerInput(ns("country"), NULL, choices = COUNTRY_CHOICES, selected = "DE"))),
    fluidRow(
      box(width = 6, title = "Energy mix over time (stacked area)", status = "success", solidHeader = TRUE,
          plotlyOutput(ns("area"), height = "380px")),
      box(width = 6, title = "Energy flow (Sankey)", status = "success", solidHeader = TRUE,
          plotlyOutput(ns("sankey"), height = "380px"))
    ),
    fluidRow(
      box(width = 12, title = "Renewable share — calendar heatmap (by year/quarter, illustrative)",
          status = "primary", solidHeader = TRUE, plotlyOutput(ns("calendar"), height = "260px"))
    )
  )
}

mod_energy_mix_server <- function(id, co2_energy_data, lang) {
  moduleServer(id, function(input, output, session) {

    d <- reactive({ co2_energy_data() %>% filter(country_code == input$country) %>% arrange(year) })

    output$area <- renderPlotly({
      x <- d()
      plot_ly(x, x = ~year, y = ~renewable_share_pct, type = "scatter", mode = "none",
              stackgroup = "one", name = "Renewable", fillcolor = THEME$risk_low) %>%
        add_trace(y = ~fossil_share_pct, name = "Fossil", fillcolor = THEME$risk_high) %>%
        add_trace(y = ~nuclear_share_pct, name = "Nuclear", fillcolor = THEME$accent) %>%
        layout(yaxis = list(title = "%"), xaxis = list(title = ""))
    })

    output$sankey <- renderPlotly({
      x <- d() %>% filter(year == max(year))
      plot_ly(
        type = "sankey",
        node = list(label = c("Renewable", "Fossil", "Nuclear", "Grid"),
                    color = c(THEME$risk_low, THEME$risk_high, THEME$accent, THEME$primary)),
        link = list(source = c(0, 1, 2), target = c(3, 3, 3),
                    value = c(x$renewable_share_pct, x$fossil_share_pct, x$nuclear_share_pct))
      )
    })

    output$calendar <- renderPlotly({
      x <- d()
      plot_ly(x, x = ~year, y = ~1, z = ~renewable_share_pct, type = "heatmap", colorscale = "Greens")
    })
  })
}

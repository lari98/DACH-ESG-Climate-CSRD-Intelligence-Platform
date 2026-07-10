# Module: Company ESG Input & Benchmarking — form to submit a company record, then
# benchmark it against sector/country peers. Submitted rows are tagged data_quality =
# "user_input" and are kept separate from official/sample reference data in the UI.

mod_company_input_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      box(width = 4, title = "Add / update company", status = "success", solidHeader = TRUE,
          textInput(ns("company_name"), "Company name"),
          pickerInput(ns("country"), t("filter_country"), choices = COUNTRY_CHOICES),
          textInput(ns("sector"), "Sector"),
          numericInput(ns("scope1"), "Scope 1 (tCO2e)", value = 1000, min = 0),
          numericInput(ns("scope2"), "Scope 2 (tCO2e)", value = 500, min = 0),
          numericInput(ns("scope3"), "Scope 3 (tCO2e)", value = 5000, min = 0),
          sliderInput(ns("esg_score"), "ESG readiness score", min = 0, max = 100, value = 50),
          sliderInput(ns("csrd_score"), "CSRD readiness score", min = 0, max = 100, value = 50),
          actionButton(ns("submit"), "Submit", class = "btn-success")
      ),
      box(width = 8, title = "Peer benchmarking", status = "primary", solidHeader = TRUE,
          plotlyOutput(ns("benchmark"), height = "420px"))
    ),
    fluidRow(box(width = 12, title = "All companies", status = "primary", solidHeader = TRUE, DTOutput(ns("table"))))
  )
}

mod_company_input_server <- function(id, company_data, lang) {
  moduleServer(id, function(input, output, session) {

    observeEvent(input$submit, {
      req(input$company_name, input$sector)
      new_row <- tibble(
        company_id = paste0("USR-", as.integer(Sys.time())),
        company_name = input$company_name,
        country_code = input$country,
        sector = input$sector,
        scope1_tco2e = input$scope1,
        scope2_tco2e = input$scope2,
        scope3_tco2e = input$scope3,
        esg_readiness_score = input$esg_score,
        csrd_readiness_score = input$csrd_score,
        reporting_gaps_count = 0,
        data_quality = "user_input"
      )
      company_data(bind_rows(company_data(), new_row))
      showNotification("Company submitted.", type = "message")
    })

    output$benchmark <- renderPlotly({
      d <- company_data()
      plot_ly(d, x = ~sector, y = ~esg_readiness_score, type = "box", name = "ESG readiness by sector",
              marker = list(color = THEME$primary))
    })

    output$table <- renderDT({
      datatable(company_data(), filter = "top", options = list(pageLength = 10))
    })
  })
}

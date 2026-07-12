# Module: Company ESG Input & Benchmarking — form to submit a company record, then
# benchmark it against sector/country peers. Submitted rows are tagged data_quality =
# "user_input" and are kept separate from official/sample reference data in the UI.

mod_company_input_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      box(width = 4, title = textOutput(ns("add_company_title")), status = "success", solidHeader = TRUE,
          textInput(ns("company_name"), NULL),
          pickerInput(ns("country"), NULL, choices = COUNTRY_CHOICES),
          textInput(ns("sector"), NULL),
          numericInput(ns("scope1"), NULL, value = 1000, min = 0),
          numericInput(ns("scope2"), NULL, value = 500, min = 0),
          numericInput(ns("scope3"), NULL, value = 5000, min = 0),
          sliderInput(ns("esg_score"), NULL, min = 0, max = 100, value = 50),
          sliderInput(ns("csrd_score"), NULL, min = 0, max = 100, value = 50),
          actionButton(ns("submit"), "Submit", class = "btn-success")
      ),
      box(width = 8, title = textOutput(ns("benchmark_title")), status = "primary", solidHeader = TRUE,
          plotlyOutput(ns("benchmark"), height = "420px"))
    ),
    fluidRow(box(width = 12, title = textOutput(ns("all_companies_title")), status = "primary", solidHeader = TRUE, DTOutput(ns("table"))))
  )
}

mod_company_input_server <- function(id, company_data, lang) {
  moduleServer(id, function(input, output, session) {

    output$add_company_title <- renderText({ t("panel_add_company", lang()) })
    output$benchmark_title <- renderText({ t("panel_peer_benchmark", lang()) })
    output$all_companies_title <- renderText({ t("table_all_companies", lang()) })

    observe({
      updateActionButton(session, "submit", label = t("btn_submit", lang()))
      updateTextInput(session, "company_name", label = t("lbl_company_name", lang()))
      updatePickerInput(session, "country", label = t("filter_country", lang()))
      updateTextInput(session, "sector", label = t("filter_sector", lang()))
      updateNumericInput(session, "scope1", label = t("lbl_scope1", lang()))
      updateNumericInput(session, "scope2", label = t("lbl_scope2", lang()))
      updateNumericInput(session, "scope3", label = t("lbl_scope3", lang()))
      updateSliderInput(session, "esg_score", label = t("lbl_esg_readiness_score", lang()))
      updateSliderInput(session, "csrd_score", label = t("lbl_csrd_readiness_score", lang()))
    })

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
      showNotification(t("notif_company_submitted", lang()), type = "message")
    })

    output$benchmark <- renderPlotly({
      d <- company_data()
      plot_ly(d, x = ~sector, y = ~esg_readiness_score, type = "box", name = t("series_esg_by_sector", lang()),
              marker = list(color = THEME$primary))
    })

    output$table <- renderDT({
      datatable(company_data(), filter = "top", options = list(pageLength = 10))
    })
  })
}

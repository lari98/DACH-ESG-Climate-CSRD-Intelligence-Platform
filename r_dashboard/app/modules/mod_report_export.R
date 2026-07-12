# Module: Report Export & Audit View — rmarkdown-driven PDF/HTML export + audit trail table.

mod_report_export_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      box(width = 4, title = textOutput(ns("export_report_title")), status = "success", solidHeader = TRUE,
          pickerInput(ns("country"), NULL, choices = COUNTRY_CHOICES),
          radioButtons(ns("format"), NULL, choices = c("HTML" = "html_document", "PDF" = "pdf_document")),
          downloadButton(ns("download_report"), t("btn_export"))),
      box(width = 8, title = textOutput(ns("audit_trail_title")), status = "primary", solidHeader = TRUE,
          DTOutput(ns("audit_table")))
    ),
    fluidRow(
      box(width = 12, title = textOutput(ns("export_raw_title")), status = "primary", solidHeader = TRUE,
          downloadButton(ns("download_co2"), textOutput(ns("btn_co2_label"), inline = TRUE)),
          downloadButton(ns("download_risk"), textOutput(ns("btn_risk_label"), inline = TRUE)),
          downloadButton(ns("download_companies"), textOutput(ns("btn_companies_label"), inline = TRUE)))
    )
  )
}

mod_report_export_server <- function(id, co2_energy_data, climate_risk_data, company_data, lang) {
  moduleServer(id, function(input, output, session) {

    output$export_report_title <- renderText({ t("panel_export_report", lang()) })
    output$audit_trail_title <- renderText({ t("panel_audit_trail", lang()) })
    output$export_raw_title <- renderText({ t("panel_export_raw", lang()) })
    output$btn_co2_label <- renderText({ t("btn_download_co2", lang()) })
    output$btn_risk_label <- renderText({ t("btn_download_risk", lang()) })
    output$btn_companies_label <- renderText({ t("btn_download_companies", lang()) })

    observe({
      updatePickerInput(session, "country", label = t("filter_country", lang()))
      updateRadioButtons(session, "format", label = t("lbl_format", lang()),
                          choices = c("HTML" = "html_document", "PDF" = "pdf_document"))
    })

    output$audit_table <- renderDT({
      d <- co2_energy_data()
      audit <- d %>% distinct(country_code, data_quality) %>%
        mutate(last_checked = as.character(Sys.time()))
      datatable(audit, options = list(dom = "t"), rownames = FALSE)
    })

    output$download_report <- downloadHandler(
      filename = function() paste0("csrd_report_", input$country, "_", Sys.Date(),
                                    if (input$format == "pdf_document") ".pdf" else ".html"),
      content = function(file) {
        rmarkdown::render(
          "reports/csrd_report_template.Rmd", output_file = file, output_format = input$format,
          params = list(country = input$country, lang = lang(),
                        co2_data = co2_energy_data(), risk_data = climate_risk_data(),
                        company_data = company_data()),
          envir = new.env()
        )
      }
    )

    output$download_co2 <- downloadHandler(
      filename = function() "co2_energy.csv",
      content = function(file) write.csv(co2_energy_data(), file, row.names = FALSE))
    output$download_risk <- downloadHandler(
      filename = function() "climate_risk.csv",
      content = function(file) write.csv(climate_risk_data(), file, row.names = FALSE))
    output$download_companies <- downloadHandler(
      filename = function() "company_esg.csv",
      content = function(file) write.csv(company_data(), file, row.names = FALSE))
  })
}

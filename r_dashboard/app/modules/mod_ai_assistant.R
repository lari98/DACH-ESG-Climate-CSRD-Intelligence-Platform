# Module: AI ESG Assistant — bilingual NL Q&A + structured insight panels, backed by
# the FastAPI /api/v1/ai endpoints (python/app/ai). Falls back to a local templated
# response if the API/LLM is unreachable, so the tab never shows a dead end.

mod_ai_assistant_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      box(width = 12, title = "Ask the ESG / CSRD assistant", status = "success", solidHeader = TRUE,
          textAreaInput(ns("question"), NULL, placeholder = "", width = "100%", rows = 2),
          actionButton(ns("ask"), "Ask", class = "btn-success"),
          hr(),
          uiOutput(ns("answer")))
    ),
    fluidRow(
      box(width = 6, title = "CSRD readiness assistant", status = "primary", solidHeader = TRUE,
          pickerInput(ns("company_id"), "Company", choices = NULL),
          uiOutput(ns("csrd_summary"))),
      box(width = 6, title = "Anomaly explanation", status = "warning", solidHeader = TRUE,
          uiOutput(ns("anomaly_panel")))
    )
  )
}

mod_ai_assistant_server <- function(id, co2_energy_data, climate_risk_data, company_data, lang) {
  moduleServer(id, function(input, output, session) {

    observe({
      updateTextAreaInput(session, "question", placeholder = t("ai_ask_placeholder", lang()))
      updatePickerInput(session, "company_id",
                         choices = setNames(company_data()$company_id, company_data()$company_name))
    })

    ai_call <- function(path, body) {
      url <- paste0(API_BASE, path)
      tryCatch({
        resp <- httr::POST(url, body = body, encode = "json", httr::timeout(8))
        if (httr::status_code(resp) != 200) stop("non-200")
        jsonlite::fromJSON(httr::content(resp, as = "text", encoding = "UTF-8"))
      }, error = function(e) NULL)
    }

    answer_text <- eventReactive(input$ask, {
      req(input$question)
      result <- ai_call("/api/v1/ai/ask", list(question = input$question, lang = lang()))
      if (!is.null(result) && !is.null(result$answer)) return(result$answer)
      # Local fallback: rule-based canned response so the tab still works offline.
      if (lang() == "de") {
        "KI-Dienst nicht erreichbar (Offline-Fallback). Bitte prüfen Sie die FastAPI-Verbindung (python/app/api). Allgemeine Antwort: DACH-CO2-Emissionen sinken seit 2000 in allen drei Ländern, angetrieben durch den Ausbau erneuerbarer Energien."
      } else {
        "AI service unreachable (offline fallback). Check the FastAPI connection (python/app/api). General answer: DACH CO2 emissions have declined across all three countries since 2000, driven by renewable energy expansion."
      }
    })

    output$answer <- renderUI({ p(answer_text()) })

    output$csrd_summary <- renderUI({
      req(input$company_id)
      d <- company_data() %>% filter(company_id == input$company_id)
      req(nrow(d) > 0)
      result <- ai_call("/api/v1/ai/csrd-readiness", list(company_id = input$company_id, lang = lang()))
      if (!is.null(result) && !is.null(result$summary)) return(p(result$summary))
      gaps <- d$reporting_gaps_count[1]
      score <- d$csrd_readiness_score[1]
      msg <- if (lang() == "de") {
        sprintf("%s hat eine CSRD-Bereitschaft von %.0f%% mit %d offenen Berichtslücken.", d$company_name[1], score, gaps)
      } else {
        sprintf("%s has CSRD readiness of %.0f%% with %d open reporting gaps.", d$company_name[1], score, gaps)
      }
      p(msg)
    })

    output$anomaly_panel <- renderUI({
      d <- co2_energy_data() %>% group_by(country_code) %>% arrange(year) %>%
        mutate(yoy = (co2_emissions_mt - lag(co2_emissions_mt)) / lag(co2_emissions_mt) * 100) %>%
        filter(!is.na(yoy)) %>% filter(abs(yoy) == max(abs(yoy), na.rm = TRUE)) %>% ungroup() %>% slice(1)
      if (nrow(d) == 0) return(NULL)
      msg <- if (lang() == "de") {
        sprintf("Größte Jahresveränderung: %s %d mit %.1f%% CO2-Änderung.", d$country_code, d$year, d$yoy)
      } else {
        sprintf("Largest year-over-year change: %s %d with a %.1f%% CO2 shift.", d$country_code, d$year, d$yoy)
      }
      p(msg)
    })
  })
}

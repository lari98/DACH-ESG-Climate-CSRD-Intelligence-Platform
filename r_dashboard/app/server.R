# server.R — app-level reactive state (language, theme) + wires every module server.

server <- function(input, output, session) {

  # --- Language state, toggled by the header button ---
  current_lang <- reactiveVal("en")
  observeEvent(input$lang_toggle_btn, {
    new_lang <- if (current_lang() == "en") "de" else "en"
    current_lang(new_lang)
    updateActionButton(session, "lang_toggle_btn", label = if (new_lang == "en") "DE" else "EN")
  })
  lang <- reactive({ current_lang() })

  # --- Restore last-selected sidebar tab (sent by JS in ui.R from localStorage) ---
  observeEvent(input$restore_tab, {
    updateTabItems(session, "main_menu", selected = input$restore_tab)
  })

  # --- Dark / light mode ---
  observeEvent(input$dark_mode, {
    if (isTRUE(input$dark_mode)) {
      shinyjs::addClass(selector = "body", class = "dark-mode")
    } else {
      shinyjs::removeClass(selector = "body", class = "dark-mode")
    }
  })

  # --- Sidebar label outputs (re-rendered whenever language changes) ---
  output$lbl_tab_overview      <- renderUI(t("tab_overview", lang()))
  output$lbl_tab_comparison    <- renderUI(t("tab_comparison", lang()))
  output$lbl_tab_map           <- renderUI(t("tab_map", lang()))
  output$lbl_tab_esg_csrd      <- renderUI(t("tab_esg_csrd", lang()))
  output$lbl_tab_forecast_lab  <- renderUI(t("tab_forecast_lab", lang()))
  output$lbl_tab_scope         <- renderUI(t("tab_scope", lang()))
  output$lbl_tab_energy_mix    <- renderUI(t("tab_energy_mix", lang()))
  output$lbl_tab_company_input <- renderUI(t("tab_company_input", lang()))
  output$lbl_tab_ai_assistant  <- renderUI(t("tab_ai_assistant", lang()))
  output$lbl_tab_report_export <- renderUI(t("tab_report_export", lang()))

  output$lbl_sub_co2      <- renderUI(t("sub_co2_predictor", lang()))
  output$lbl_sub_renew    <- renderUI(t("sub_renewable_pred", lang()))
  output$lbl_sub_price    <- renderUI(t("sub_price_predictor", lang()))
  output$lbl_sub_risk     <- renderUI(t("sub_climate_risk_pred", lang()))
  output$lbl_sub_esg      <- renderUI(t("sub_esg_readiness_pred", lang()))
  output$lbl_sub_scope    <- renderUI(t("sub_scope_forecast", lang()))
  output$lbl_sub_scenario <- renderUI(t("sub_scenario_sim", lang()))

  # --- Shared datasets, loaded once per session ---
  co2_energy_data   <- reactive({ load_co2_energy() })
  climate_risk_data <- reactive({ load_climate_risk() })
  company_data       <- reactiveVal(load_companies())  # reactiveVal: company_input module can append rows

  # --- Wire every module server, passing shared reactives + language ---
  mod_executive_overview_server("overview", co2_energy_data, climate_risk_data, company_data, lang)
  mod_country_comparison_server("comparison", co2_energy_data, lang)
  mod_climate_map_server("map", climate_risk_data, co2_energy_data, lang)
  mod_esg_csrd_server("esg_csrd", company_data, lang)

  mod_forecast_co2_server("sub_co2", co2_energy_data, lang)
  mod_forecast_renewable_server("sub_renew", co2_energy_data, lang)
  mod_forecast_price_server("sub_price", co2_energy_data, lang)
  mod_forecast_risk_server("sub_risk", climate_risk_data, lang)
  mod_forecast_esg_server("sub_esg", company_data, lang)
  mod_forecast_scope_server("sub_scope", company_data, lang)
  mod_forecast_scenario_server("sub_scenario", co2_energy_data, lang)

  mod_scope_emissions_server("scope", company_data, lang)
  mod_energy_mix_server("energy_mix", co2_energy_data, lang)
  mod_company_input_server("company_input", company_data, lang)
  mod_ai_assistant_server("ai_assistant", co2_energy_data, climate_risk_data, company_data, lang)
  mod_report_export_server("report_export", co2_energy_data, climate_risk_data, company_data, lang)
}

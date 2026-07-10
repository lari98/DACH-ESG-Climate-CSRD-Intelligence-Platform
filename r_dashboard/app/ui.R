# ui.R — enterprise DACH shell: sidebar with 10 main tabs, EN/DE + dark/light toggles.

header <- dashboardHeader(
  title = span(id = "app_title_text", "DACH ESG & CSRD Platform"),
  tags$li(class = "dropdown", style = "padding: 8px 12px;",
          prettySwitch(inputId = "dark_mode", label = "", value = FALSE, status = "success", fill = TRUE)),
  tags$li(class = "dropdown", style = "padding: 8px 12px;",
          actionButton("lang_toggle_btn", label = "DE", class = "btn-sm lang-toggle-btn"))
)

sidebar <- dashboardSidebar(
  width = 300,
  sidebarMenu(
    id = "main_menu",
    menuItem(uiOutput("lbl_tab_overview", inline = TRUE),      tabName = "overview",      icon = icon("gauge-high")),
    menuItem(uiOutput("lbl_tab_comparison", inline = TRUE),    tabName = "comparison",    icon = icon("scale-balanced")),
    menuItem(uiOutput("lbl_tab_map", inline = TRUE),           tabName = "map",           icon = icon("earth-europe")),
    menuItem(uiOutput("lbl_tab_esg_csrd", inline = TRUE),      tabName = "esg_csrd",      icon = icon("clipboard-check")),
    menuItem(uiOutput("lbl_tab_forecast_lab", inline = TRUE),  tabName = "forecast_lab",  icon = icon("chart-line"),
             menuSubItem(uiOutput("lbl_sub_co2", inline = TRUE), tabName = "sub_co2"),
             menuSubItem(uiOutput("lbl_sub_renew", inline = TRUE), tabName = "sub_renew"),
             menuSubItem(uiOutput("lbl_sub_price", inline = TRUE), tabName = "sub_price"),
             menuSubItem(uiOutput("lbl_sub_risk", inline = TRUE), tabName = "sub_risk"),
             menuSubItem(uiOutput("lbl_sub_esg", inline = TRUE), tabName = "sub_esg"),
             menuSubItem(uiOutput("lbl_sub_scope", inline = TRUE), tabName = "sub_scope"),
             menuSubItem(uiOutput("lbl_sub_scenario", inline = TRUE), tabName = "sub_scenario")),
    menuItem(uiOutput("lbl_tab_scope", inline = TRUE),         tabName = "scope",         icon = icon("industry")),
    menuItem(uiOutput("lbl_tab_energy_mix", inline = TRUE),    tabName = "energy_mix",    icon = icon("bolt")),
    menuItem(uiOutput("lbl_tab_company_input", inline = TRUE), tabName = "company_input", icon = icon("building")),
    menuItem(uiOutput("lbl_tab_ai_assistant", inline = TRUE),  tabName = "ai_assistant",  icon = icon("robot")),
    menuItem(uiOutput("lbl_tab_report_export", inline = TRUE), tabName = "report_export", icon = icon("file-export"))
  )
)

body <- dashboardBody(
  useShinyjs(),
  tags$head(tags$link(rel = "stylesheet", type = "text/css", href = "custom.css")),
  # Remember the selected sidebar tab across page reloads (e.g. shiny.autoreload
  # restarts, which otherwise always drop the user back on the first tab, since a
  # full app/browser reload has no server-side session to resume from).
  tags$script(HTML("
    $(document).on('shiny:connected', function() {
      var saved = localStorage.getItem('dach_esg_last_tab');
      if (saved) {
        Shiny.setInputValue('restore_tab', saved);
      }
    });
    $(document).on('shown.bs.tab', 'a[data-toggle=\"tab\"]', function(e) {
      var tabName = $(e.target).attr('data-value');
      if (tabName) localStorage.setItem('dach_esg_last_tab', tabName);
    });
  ")),
  tabItems(
    tabItem("overview",      mod_executive_overview_ui("overview")),
    tabItem("comparison",    mod_country_comparison_ui("comparison")),
    tabItem("map",           mod_climate_map_ui("map")),
    tabItem("esg_csrd",      mod_esg_csrd_ui("esg_csrd")),
    tabItem("sub_co2",       mod_forecast_co2_ui("sub_co2")),
    tabItem("sub_renew",     mod_forecast_renewable_ui("sub_renew")),
    tabItem("sub_price",     mod_forecast_price_ui("sub_price")),
    tabItem("sub_risk",      mod_forecast_risk_ui("sub_risk")),
    tabItem("sub_esg",       mod_forecast_esg_ui("sub_esg")),
    tabItem("sub_scope",     mod_forecast_scope_ui("sub_scope")),
    tabItem("sub_scenario",  mod_forecast_scenario_ui("sub_scenario")),
    tabItem("scope",         mod_scope_emissions_ui("scope")),
    tabItem("energy_mix",    mod_energy_mix_ui("energy_mix")),
    tabItem("company_input", mod_company_input_ui("company_input")),
    tabItem("ai_assistant",  mod_ai_assistant_ui("ai_assistant")),
    tabItem("report_export", mod_report_export_ui("report_export"))
  )
)

ui <- dashboardPage(
  title = "DACH ESG, Climate Risk & CSRD Intelligence Platform",
  header, sidebar, body,
  skin = "green"
)

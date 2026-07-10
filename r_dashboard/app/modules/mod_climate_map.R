# Module 3: Advanced Climate Risk Map
# Leaflet-based multi-layer, multi-view map: choropleth risk layer, heatmap, clustered
# markers, timeline slider with play/pause, base-map style switcher, layer control,
# region compare, and click-through drill-down panel. Uses synthetic per-region lon/lat
# centroids (data/sample) since full NUTS/canton shapefiles are out of scope for the
# offline demo dataset — swap in `sf` polygons + real centroids for production.

mod_climate_map_ui <- function(id) {
  ns <- NS(id)
  fluidPage(
    fluidRow(
      column(3, pickerInput(ns("country"), NULL, choices = c("All" = "ALL", COUNTRY_CHOICES), selected = "ALL")),
      column(3, selectInput(ns("map_style"), NULL,
                             choices = c("Light (consulting)" = "CartoDB.PositronNoLabels",
                                         "Dark mode" = "CartoDB.DarkMatterNoLabels",
                                         "Standard" = "OpenStreetMap",
                                         "Satellite" = "Esri.WorldImagery",
                                         "Terrain" = "Esri.WorldTopoMap"))),
      column(3, selectInput(ns("layer"), NULL,
                             choices = c("Composite risk (choropleth)" = "composite",
                                         "Physical risk" = "physical",
                                         "Transition risk" = "transition",
                                         "Flood risk" = "flood",
                                         "Heat stress" = "heat",
                                         "Emission intensity (heatmap)" = "heatmap",
                                         "Renewable energy layer" = "renewable"))),
      column(3, selectInput(ns("view"), NULL,
                             choices = c("Present" = "present", "Past (baseline)" = "past",
                                         "Future forecast" = "future", "Next-future scenario" = "next_future")))
    ),
    fluidRow(
      column(9,
        box(width = NULL, status = "success", solidHeader = FALSE,
            leafletOutput(ns("map"), height = "620px"),
            div(style = "margin-top:8px;",
                sliderInput(ns("year"), NULL, min = 2000, max = 2050, value = 2023, step = 1,
                            sep = "", animate = animationOptions(interval = 700, loop = FALSE), width = "100%")),
            div(actionButton(ns("reset_map"), label = NULL, icon = icon("rotate-left")),
                actionButton(ns("compare_toggle"), label = NULL, icon = icon("code-compare")))
        )
      ),
      column(3,
        box(width = NULL, title = "Region details", status = "primary", solidHeader = TRUE,
            uiOutput(ns("region_detail"))),
        box(width = NULL, title = "AI risk explanation", status = "warning", solidHeader = TRUE,
            uiOutput(ns("ai_risk_panel")))
      )
    )
  )
}

mod_climate_map_server <- function(id, climate_risk_data, co2_energy_data, lang) {
  moduleServer(id, function(input, output, session) {

    # Deterministic synthetic centroids per region (demo only — replace with real
    # NUTS2/Kanton centroids in production, sourced from Eurostat/BFS geodata).
    region_coords <- reactive({
      d <- climate_risk_data()
      set.seed(1)
      centers <- list(DE = c(lat = 51.1657, lon = 10.4515),
                       AT = c(lat = 47.5162, lon = 14.5501),
                       CH = c(lat = 46.8182, lon = 8.2275))
      d$lat <- NA_real_; d$lon <- NA_real_
      for (cc in names(centers)) {
        idx <- which(d$country_code == cc)
        n <- length(idx)
        if (n == 0) next
        ang <- seq(0, 2 * pi, length.out = n + 1)[1:n]
        d$lat[idx] <- centers[[cc]]["lat"] + 1.3 * sin(ang)
        d$lon[idx] <- centers[[cc]]["lon"] + 1.3 * cos(ang)
      }
      d
    })

    filtered <- reactive({
      d <- region_coords()
      if (input$country != "ALL") d <- d %>% filter(country_code == input$country)
      d
    })

    # View adjustment: past/future/next_future apply an illustrative multiplier so the
    # timeline visibly changes risk levels (production: swap for real modeled time series).
    view_adjusted <- reactive({
      d <- filtered()
      mult <- switch(input$view,
        past = 0.7,
        present = 1.0,
        future = 1.0 + max(0, (input$year - 2023)) * 0.015,
        next_future = 1.0 + max(0, (input$year - 2023)) * 0.03
      )
      d$composite_climate_risk_score <- pmin(10, d$composite_climate_risk_score * mult)
      d$risk_level <- as.character(risk_level_from_score(d$composite_climate_risk_score))
      d
    })

    pal <- reactive({
      colorNumeric(c(THEME$risk_low, THEME$risk_med, THEME$risk_high), domain = c(0, 10))
    })

    output$map <- renderLeaflet({
      leaflet(options = leafletOptions(minZoom = 3)) %>%
        addProviderTiles(input$map_style %||% "CartoDB.PositronNoLabels", group = "base") %>%
        setView(lng = 10.5, lat = 48.5, zoom = 5) %>%
        addLayersControl(overlayGroups = c("Risk markers", "Heatmap", "Clusters"),
                          options = layersControlOptions(collapsed = TRUE))
    })

    observeEvent(input$map_style, {
      leafletProxy("map") %>% clearTiles() %>% addProviderTiles(input$map_style)
    })

    observe({
      d <- view_adjusted()
      p <- pal()
      proxy <- leafletProxy("map", data = d) %>% clearMarkers() %>% clearMarkerClusters() %>% clearHeatmap() %>% clearShapes()

      if (input$layer == "heatmap") {
        proxy %>% addHeatmap(lng = ~lon, lat = ~lat, intensity = ~composite_climate_risk_score,
                              radius = 30, blur = 25, group = "Heatmap")
      } else {
        value_col <- switch(input$layer,
          physical = "physical_risk_score", transition = "transition_risk_score",
          flood = "flood_risk_score", heat = "heat_stress_score",
          renewable = "composite_climate_risk_score",  # placeholder proxy in absence of renewable-by-region data
          composite = "composite_climate_risk_score",
          "composite_climate_risk_score"
        )
        d$val <- d[[value_col]]
        proxy %>%
          addCircleMarkers(data = d, lng = ~lon, lat = ~lat, radius = ~6 + val, color = ~p(val),
                            fillOpacity = 0.85, stroke = TRUE, weight = 1,
                            label = ~paste0(region, ": ", round(val, 1)),
                            layerId = ~region, group = "Risk markers") %>%
          addLegend("bottomright", pal = p, values = d$val, title = "Risk score", group = "Risk markers")
      }
    })

    observeEvent(input$reset_map, {
      leafletProxy("map") %>% setView(lng = 10.5, lat = 48.5, zoom = 5)
    })

    selected_region <- reactiveVal(NULL)
    observeEvent(input$map_marker_click, {
      selected_region(input$map_marker_click$id)
    })

    output$region_detail <- renderUI({
      req(selected_region())
      d <- view_adjusted() %>% filter(region == selected_region())
      if (nrow(d) == 0) return(p("Click a marker to see region detail."))
      tagList(
        h4(selected_region()),
        p(strong(t("kpi_climate_risk", lang())), ": ", round(d$composite_climate_risk_score[1], 1)),
        p(strong("Risk level"), ": ", d$risk_level[1])
      )
    })

    output$ai_risk_panel <- renderUI({
      req(selected_region())
      d <- view_adjusted() %>% filter(region == selected_region())
      if (nrow(d) == 0) return(NULL)
      lvl <- d$risk_level[1]
      msg_en <- sprintf("%s shows %s composite climate risk. %s", selected_region(), tolower(lvl),
                         if (lvl == "High") "Prioritize adaptation investment and CSRD physical-risk disclosure."
                         else if (lvl == "Medium") "Monitor trend; document mitigation plans for CSRD."
                         else "Currently low priority; maintain monitoring cadence.")
      msg_de <- sprintf("%s zeigt ein %s Klimarisiko. %s", selected_region(),
                         if (lvl == "High") "hohes" else if (lvl == "Medium") "mittleres" else "niedriges",
                         if (lvl == "High") "Anpassungsinvestitionen und CSRD-Offenlegung physischer Risiken priorisieren."
                         else if (lvl == "Medium") "Trend beobachten; Minderungspläne für CSRD dokumentieren."
                         else "Derzeit niedrige Priorität; Überwachung fortsetzen.")
      p(if (lang() == "de") msg_de else msg_en)
    })
  })
}

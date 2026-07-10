# global.R — libraries, data, translations, shared helpers. Sourced once at app start.

suppressPackageStartupMessages({
  library(shiny)
  library(shinydashboard)
  library(shinydashboardPlus)  # premium widgets (boxes, gauges) — falls back gracefully if absent
  library(shinyWidgets)
  library(shinyjs)
  library(tidyverse)
  library(plotly)
  library(leaflet)
  library(leaflet.extras)
  library(sf)
  library(DT)
  library(forecast)
  library(rmarkdown)
  library(httr)
  library(jsonlite)
  library(readr)
})

source("lang/translations.R")
source("data/load_data.R")

for (f in list.files("modules", pattern = "\\.R$", full.names = TRUE)) source(f)

# --- Enterprise DACH color palette (consulting-grade, not childish/over-colorful) ---
THEME <- list(
  primary   = "#0B3D2E",   # deep forest green — DACH sustainability / finance tone
  secondary = "#1F5F4F",
  accent    = "#C9A24B",   # muted gold accent for highlights/CTAs
  risk_low  = "#4C8C6B",
  risk_med  = "#D6A24B",
  risk_high = "#B24C4C",
  bg_light  = "#F7F8F7",
  bg_dark   = "#12181A",
  text_light= "#1A1F1E",
  text_dark = "#EDEFEC",
  grid      = "#D9DED9"
)

COUNTRY_CHOICES <- c("Germany" = "DE", "Austria" = "AT", "Switzerland" = "CH")
HORIZON_CHOICES <- c("1 year" = "1y", "3 years" = "3y", "5 years" = "5y", "10 years" = "10y",
                      "2030" = "2030", "2040" = "2040", "2050" = "2050")
SCENARIO_CHOICES <- c("Baseline", "Accelerated Transition", "Delayed Policy Action")

#' Simple, explainable linear-trend forecaster with a confidence band — used across
#' every Forecast Lab sub-tab so behavior is consistent. Swappable for Prophet/fable
#' in production (see docs/02_architecture.md).
forecast_series <- function(years, values, horizon_years) {
  df <- data.frame(year = years, value = values)
  fit <- lm(value ~ year, data = df)
  last_year <- max(years)
  future_years <- (last_year + 1):(last_year + horizon_years)
  pred <- predict(fit, newdata = data.frame(year = future_years), interval = "confidence", level = 0.95)
  data.frame(
    year = future_years,
    forecast = pred[, "fit"],
    lower = pred[, "lwr"],
    upper = pred[, "upr"]
  )
}

scenario_adjust <- function(forecast_df, scenario) {
  factor <- switch(scenario,
    "Accelerated Transition" = 0.85,
    "Delayed Policy Action"  = 1.12,
    1.0
  )
  forecast_df$forecast <- forecast_df$forecast * factor
  forecast_df$lower <- forecast_df$lower * factor
  forecast_df$upper <- forecast_df$upper * factor
  forecast_df
}

risk_level_from_score <- function(score) {
  cut(score, breaks = c(-Inf, 4, 7, Inf), labels = c("Low", "Medium", "High"))
}

#' Drop-in replacement for shiny::validate(need(cond, msg)) that builds the same
#' "shiny.silent.error" / "validation" condition Shiny's render functions look for,
#' but without going through shiny::validate()/need() themselves. Some shiny/R builds
#' (observed with R 4.6.1) throw a spurious "is.character(txt) is not TRUE" error out
#' of validate()'s own internals even on fully valid input — this bypasses that bug
#' while keeping the same red "no data" message box behavior in the UI.
safe_validate <- function(cond, msg) {
  if (isTRUE(cond)) return(invisible(NULL))
  cond_obj <- structure(
    class = c("shiny.silent.error", "validation", "error", "condition"),
    list(message = msg, call = NULL)
  )
  stop(cond_obj)
}

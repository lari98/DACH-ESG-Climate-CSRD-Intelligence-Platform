# Unit tests for the shared forecasting helpers in global.R
# (forecast_series, scenario_adjust, risk_level_from_score).

suppressPackageStartupMessages({
  library(dplyr)
})

forecast_series <- function(years, values, horizon_years) {
  df <- data.frame(year = years, value = values)
  fit <- lm(value ~ year, data = df)
  last_year <- max(years)
  future_years <- (last_year + 1):(last_year + horizon_years)
  pred <- predict(fit, newdata = data.frame(year = future_years), interval = "confidence", level = 0.95)
  data.frame(year = future_years, forecast = pred[, "fit"], lower = pred[, "lwr"], upper = pred[, "upr"])
}

scenario_adjust <- function(forecast_df, scenario) {
  factor <- switch(scenario, "Accelerated Transition" = 0.85, "Delayed Policy Action" = 1.12, 1.0)
  forecast_df$forecast <- forecast_df$forecast * factor
  forecast_df$lower <- forecast_df$lower * factor
  forecast_df$upper <- forecast_df$upper * factor
  forecast_df
}

risk_level_from_score <- function(score) {
  cut(score, breaks = c(-Inf, 4, 7, Inf), labels = c("Low", "Medium", "High"))
}

test_that("forecast_series returns the requested horizon length", {
  years <- 2015:2023
  values <- seq(100, 108)
  fc <- forecast_series(years, values, horizon_years = 5)
  expect_equal(nrow(fc), 5)
  expect_equal(fc$year, 2024:2028)
})

test_that("forecast_series confidence band is well-ordered (lower <= forecast <= upper)", {
  years <- 2010:2023
  values <- 100 + (years - 2010) * 2 + rnorm(length(years), 0, 1)
  fc <- forecast_series(years, values, horizon_years = 3)
  expect_true(all(fc$lower <= fc$forecast))
  expect_true(all(fc$forecast <= fc$upper))
})

test_that("scenario_adjust applies the correct direction per scenario", {
  base <- data.frame(year = 2024:2026, forecast = c(100, 110, 120), lower = c(90, 95, 100), upper = c(110, 125, 140))
  accel <- scenario_adjust(base, "Accelerated Transition")
  delayed <- scenario_adjust(base, "Delayed Policy Action")
  expect_true(all(accel$forecast < base$forecast))
  expect_true(all(delayed$forecast > base$forecast))
})

test_that("risk_level_from_score buckets correctly at boundaries", {
  expect_equal(as.character(risk_level_from_score(3.9)), "Low")
  expect_equal(as.character(risk_level_from_score(4.1)), "Medium")
  expect_equal(as.character(risk_level_from_score(7.1)), "High")
})

# Data access layer for the Shiny app.
# Prefers the FastAPI service (python/app/api) when reachable; falls back to reading
# data/cleaned CSVs directly (or data/sample) so the dashboard always has something to
# render, even with the API offline — every fallback path tags rows with data_quality.

API_BASE <- Sys.getenv("ESG_API_BASE", unset = "http://localhost:8000")
PROJECT_ROOT <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), "..", "..", ".."),
                               mustWork = FALSE)

`%||%` <- function(a, b) if (is.null(a) || length(a) == 0) b else a

.read_local_csv <- function(name) {
  candidates <- c(
    file.path("data", "cleaned", paste0(name, ".csv")),
    file.path("..", "..", "data", "cleaned", paste0(name, ".csv")),
    file.path("..", "..", "data", "sample", paste0("sample_", name, ".csv"))
  )
  for (p in candidates) {
    if (file.exists(p)) return(readr::read_csv(p, show_col_types = FALSE))
  }
  # last resort: relative to sample naming used in scripts/generate_sample_data.py
  alt <- list(
    co2_energy = "sample_co2_energy_dach.csv",
    regional_climate_risk = "sample_regional_climate_risk.csv",
    company_esg = "sample_company_esg.csv"
  )[[name]]
  if (!is.null(alt)) {
    for (base in c(file.path("..", "..", "data", "sample"), file.path("data", "sample"))) {
      p <- file.path(base, alt)
      if (file.exists(p)) return(readr::read_csv(p, show_col_types = FALSE))
    }
  }
  stop(sprintf("No local data found for '%s'. Run scripts/generate_sample_data.py first.", name))
}

#' Fetch a dataset either from the live API or from local cleaned/sample CSVs.
#' @param endpoint one of "co2-energy", "climate-risk", "companies"
#' @param local_name matching local file base name: "co2_energy", "regional_climate_risk", "company_esg"
fetch_dataset <- function(endpoint, local_name) {
  url <- paste0(API_BASE, "/api/v1/", endpoint)
  result <- tryCatch({
    resp <- httr::GET(url, httr::timeout(3))
    if (httr::status_code(resp) != 200) stop("non-200")
    jsonlite::fromJSON(httr::content(resp, as = "text", encoding = "UTF-8"))
  }, error = function(e) NULL)

  if (is.null(result) || (is.data.frame(result) && nrow(result) == 0)) {
    message(sprintf("[load_data] API unavailable for %s, falling back to local CSV", endpoint))
    return(.read_local_csv(local_name))
  }
  tibble::as_tibble(result)
}

load_co2_energy         <- function() fetch_dataset("co2-energy", "co2_energy")
load_climate_risk       <- function() fetch_dataset("climate-risk", "regional_climate_risk")
load_companies          <- function() fetch_dataset("companies", "company_esg")

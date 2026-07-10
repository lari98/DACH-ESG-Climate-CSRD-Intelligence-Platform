# Run once: Rscript install_packages.R
pkgs <- c(
  "shiny", "shinydashboard", "shinydashboardPlus", "shinyWidgets", "shinyjs",
  "tidyverse", "plotly", "leaflet", "leaflet.extras", "sf", "DT",
  "forecast", "prophet", "fable", "rmarkdown", "httr", "jsonlite", "readr"
)
installed <- rownames(installed.packages())
to_install <- setdiff(pkgs, installed)
if (length(to_install) > 0) install.packages(to_install, repos = "https://cloud.r-project.org")
cat("All required packages installed.\n")

# Phase 10: R dashboard test runner. Run with: Rscript tests/testthat.R
# (from the r_dashboard/ directory)
library(testthat)

test_check_dir <- file.path(dirname(sys.frame(1)$ofile %||% "tests"), "testthat")
`%||%` <- function(a, b) if (is.null(a)) b else a

test_dir("tests/testthat", reporter = "summary")

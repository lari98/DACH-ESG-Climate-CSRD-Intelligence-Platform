# Unit tests for the EN/DE translation dictionary (lang/translations.R).
# Run via: Rscript tests/testthat.R  (from r_dashboard/)

source(file.path("..", "app", "lang", "translations.R"))

test_that("every translation key has both en and de entries", {
  missing <- character(0)
  for (key in names(TRANSLATIONS)) {
    entry <- TRANSLATIONS[[key]]
    if (is.null(entry$en) || is.null(entry$de)) missing <- c(missing, key)
  }
  expect_equal(missing, character(0))
})

test_that("t() returns the correct language string", {
  expect_equal(t("tab_overview", "en"), "Executive Overview")
  expect_equal(t("tab_overview", "de"), "Management-Übersicht")
})

test_that("t() falls back to English for unknown language codes", {
  expect_equal(t("tab_overview", "fr"), "Executive Overview")
})

test_that("t() returns the key itself for unknown keys (no crash)", {
  expect_equal(t("not_a_real_key", "en"), "not_a_real_key")
})

test_that("en and de translations are never identical for user-facing tab labels", {
  tab_keys <- grep("^tab_", names(TRANSLATIONS), value = TRUE)
  identical_pairs <- Filter(function(k) TRANSLATIONS[[k]]$en == TRANSLATIONS[[k]]$de, tab_keys)
  expect_equal(identical_pairs, character(0))
})

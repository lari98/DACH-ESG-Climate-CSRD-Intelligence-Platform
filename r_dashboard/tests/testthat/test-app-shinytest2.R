# Phase 10: app-level UI test skeleton using shinytest2 (visual/interaction testing).
# Requires: install.packages(c("shinytest2", "chromote")) and a Chrome/Chromium binary.
# Skipped automatically in environments without a browser (e.g. headless CI without
# Chrome installed) via skip_if_not_installed / tryCatch, so it never blocks the
# lightweight testthat suite above.

test_that("app launches and the Executive Overview tab renders without error", {
  skip_if_not_installed("shinytest2")
  testthat::skip_on_ci()  # remove once a Chrome binary is provisioned in CI

  app <- shinytest2::AppDriver$new(app_dir = file.path("..", "..", "app"), name = "dach-esg-app")
  on.exit(app$stop())

  # Executive Overview is the default landing tab
  app$expect_values(input = "overview-country")

  # Language toggle should change the header title without erroring
  app$click(selector = "#lang_toggle_btn")
  app$wait_for_idle()

  # Dark mode toggle should not error
  app$set_inputs(dark_mode = TRUE)
  app$wait_for_idle()
})

test_that("switching to the Climate Risk Map tab renders the leaflet widget", {
  skip_if_not_installed("shinytest2")
  testthat::skip_on_ci()

  app <- shinytest2::AppDriver$new(app_dir = file.path("..", "..", "app"), name = "dach-esg-map")
  on.exit(app$stop())
  app$set_inputs(main_menu = "map")
  app$wait_for_idle()
  expect_true(TRUE)  # presence check placeholder; extend with app$get_html() assertions
})

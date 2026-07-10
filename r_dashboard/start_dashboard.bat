@echo off
REM shiny.autoreload watches every .R file under app/ and, the instant one changes on
REM disk (e.g. Claude edits a module while this is running), automatically restarts the
REM app and refreshes the browser tab - no manual stop/start needed.
cd /d "%~dp0"
set SHINY_AUTORELOAD=TRUE
R -e "options(shiny.autoreload = TRUE); shiny::runApp('app', port = 3838, launch.browser = TRUE)"

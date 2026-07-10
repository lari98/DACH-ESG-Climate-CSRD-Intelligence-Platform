@echo off
REM One-click API launcher.
REM First run: pulls live data from free public APIs (OWID, Eurostat), cleans it,
REM loads it into the local SQLite DB, then starts uvicorn.
REM Every run after that: if the DB already has data, skips straight to uvicorn
REM (starts in milliseconds) unless you pass "refresh" as an argument.

cd /d "%~dp0"

if "%1"=="refresh" (
    echo Refreshing data from free public APIs...
    python -m app.ingestion.run_all
    python -m app.cleaning.clean
    python -m app.db.session
) else (
    if exist "..\data\esg_platform.db" (
        echo Existing database found - skipping ingestion, starting API immediately.
    ) else (
        echo No database found yet - running one-time data pull from free public APIs...
        python -m app.ingestion.run_all
        python -m app.cleaning.clean
        python -m app.db.session
    )
)

echo Launching R Shiny dashboard in a separate window (http://127.0.0.1:3838)...
start "R Shiny Dashboard" "%~dp0..\r_dashboard\start_dashboard.bat"

echo Starting API on http://localhost:8000 (auto-reloads on file changes) ...
uvicorn app.api.main:app --port 8000 --reload --reload-dir app

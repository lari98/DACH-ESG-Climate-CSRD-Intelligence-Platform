"""Central configuration. Switches cleanly between local dev and Azure via env vars."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def _read_project_version() -> str:
    """Reads the single source of truth (VERSION file, see CHANGELOG.md) so the API's
    reported version never drifts out of sync with a hardcoded string."""
    version_file = PROJECT_ROOT / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "0.0.0-unknown"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    # Environment switch: "local" (SQLite, filesystem) or "azure" (Azure SQL, Blob)
    environment: str = "local"

    # Data mode: "sample" (bundled generated data) or "live" (pull from public sources)
    data_mode: str = "sample"

    # Background auto-refresh: when True, the API pulls fresh data (ingest -> clean ->
    # validate/reconcile -> load) automatically on startup and every auto_refresh_interval_seconds
    # after that - no manual "start_api.bat refresh" ever required. See app.core.scheduler.
    auto_refresh_enabled: bool = True
    auto_refresh_interval_seconds: int = 3600

    # Local storage
    raw_dir: Path = DATA_DIR / "raw"
    cleaned_dir: Path = DATA_DIR / "cleaned"
    sample_dir: Path = DATA_DIR / "sample"

    # Database
    # NOTE: on some networked/mounted filesystems SQLite file-locking can fail with
    # "disk I/O error". If you hit that locally, override DATABASE_URL to a path on a
    # local (non-networked) disk, e.g. DATABASE_URL=sqlite:////tmp/esg_platform.db
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'esg_platform.db'}"

    # Azure (only used when environment == "azure"; values sourced from Key Vault in real deploys)
    azure_storage_connection_string: str | None = None
    azure_sql_connection_string: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str = "gpt-4o-mini"
    azure_key_vault_url: str | None = None

    # API
    api_title: str = "DACH ESG, Climate Risk & CSRD Intelligence Platform API"
    api_version: str = _read_project_version()
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Central configuration. Switches cleanly between local dev and Azure via env vars."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")

    # Environment switch: "local" (SQLite, filesystem) or "azure" (Azure SQL, Blob)
    environment: str = "local"

    # Data mode: "sample" (bundled generated data) or "live" (pull from public sources)
    data_mode: str = "sample"

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
    api_version: str = "0.1.0"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()

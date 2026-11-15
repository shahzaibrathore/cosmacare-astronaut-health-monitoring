"""Application configuration using pydantic-settings."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CosmaCare Backend"
    database_url: str = f"sqlite:///{DATA_DIR / 'cosmacare.db'}"
    heartbeat_stale_seconds: int = 30
    enable_auto_seed: bool = True


settings = Settings()
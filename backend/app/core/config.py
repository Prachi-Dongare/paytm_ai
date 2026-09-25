from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ReconcileAI"
    app_version: str = "1.0.0"
    environment: str = "development"

    openai_api_key: str | None = None

    database_url: str = (
        "postgresql+psycopg://reconcile_user:reconcile_password"
        "@localhost:5432/reconcile_ai"
    )

    frontend_url: str = "http://localhost:3000"
    local_ai_model: str = "llama3.2:3b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
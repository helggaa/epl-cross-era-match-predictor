import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EPL Cross-Era Match Predictor"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/epl_predictor"

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Gemini / Anthropic API Key & Model (optional)
    GEMINI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    LLM_MODEL: str = "gemini-flash-lite-latest"

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

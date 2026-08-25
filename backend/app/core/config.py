from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EPL Cross-Era Match Predictor"
    VERSION: str = "0.9.0"
    API_V1_STR: str = "/api/v1"


    # Database: Defaults to SQLite file in backend/ directory, can be overridden by Neon/PostgreSQL DATABASE_URL
    DATABASE_URL: str = "sqlite:///./epl_predictor.db"

    # CORS Configuration: Comma-separated list or *
    CORS_ORIGINS: str = "*"

    # Gemini / Anthropic API Key & Model (optional)
    GEMINI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    LLM_MODEL: str = "gemini-flash-lite-latest"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        if not v:
            return "sqlite:///./epl_predictor.db"
        # Render / Neon / Heroku compatibility: convert postgres:// to postgresql://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()


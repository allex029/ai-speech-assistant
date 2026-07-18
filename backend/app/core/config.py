"""Application configuration via Pydantic Settings."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="SpeakFlow API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/speakflow",
        alias="DATABASE_URL",
    )
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # Groq / AI models
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        alias="GROQ_BASE_URL",
    )
    model_name: str = Field(
        default="llama-3.3-70b-versatile",
        alias="MODEL_NAME",
    )
    whisper_model: str = Field(
        default="whisper-large-v3-turbo",
        alias="WHISPER_MODEL",
    )
    llama_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="LLAMA_MODEL",
    )

    # Audio constraints
    max_audio_size_mb: int = Field(default=25, alias="MAX_AUDIO_SIZE_MB")
    allowed_audio_types: str = Field(
        default="audio/wav,audio/mpeg,audio/mp3,audio/webm,audio/ogg,audio/flac,audio/x-wav,audio/mp4",
        alias="ALLOWED_AUDIO_TYPES",
    )

    # Security (JWT ready for future auth)
    secret_key: str = Field(
        default="change-me-in-production-use-openssl-rand-hex-32",
        alias="SECRET_KEY",
    )
    access_token_expire_minutes: int = Field(
        default=60 * 24,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_audio_types_list(self) -> List[str]:
        return [t.strip() for t in self.allowed_audio_types.split(",") if t.strip()]

    @property
    def max_audio_size_bytes(self) -> int:
        return self.max_audio_size_mb * 1024 * 1024

    @property
    def sync_database_url(self) -> str:
        """Sync URL for Alembic migrations (asyncpg → psycopg2)."""
        return self.database_url.replace(
            "postgresql+asyncpg://",
            "postgresql+psycopg2://",
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ]
    )
    cors_origin_regex: str = r"^https?://(localhost|127\\.0\\.0\\.1)(:\\d+)?$"

    # Database (default sqlite for local MVP)
    database_url: str = "sqlite+aiosqlite:///./prism.db"

    # LLM keys (optional in MVP)
    anthropic_api_key: str = ""
    openai_api_key: str = ""


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    database_url: str = "postgresql://user:pass@localhost:5432/prism"
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

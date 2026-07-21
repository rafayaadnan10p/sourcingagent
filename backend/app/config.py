from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Always resolve .env relative to this file (backend/.env), regardless of cwd
_ENV_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Serper
    serper_api_key: str

    # Database
    database_url: str

    # CORS — comma-separated origins stored as a single string in .env
    allowed_origins: str = "http://localhost:5173"

    # Rate limiting
    rate_limit_per_minute: int = 10

    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()

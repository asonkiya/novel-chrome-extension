from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---- Core App ----
    APP_NAME: str = "Novel Translator API"
    ENV: str = "development"

    # ---- Database ----
    DATABASE_URL: str

    # ---- OpenAI ----
    OPENAI_API_KEY: str

    # ---- Optional future config ----
    DEFAULT_SOURCE_LANG: str = "ko"
    DEFAULT_TARGET_LANG: str = "en"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Prevents re-reading environment repeatedly.
    """
    return Settings()


settings = get_settings()

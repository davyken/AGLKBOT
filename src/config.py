from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_WHISPER_MODEL: str = "whisper-1"
    MONGODB_URI: str = ""
    DATABASE_URL: str = ""
    BACKEND_URL: str = ""

    BOT_NAME: str = "Amara"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

"""Configuration for the Telegram bot."""
from __future__ import annotations

from pydantic import AnyHttpUrl, BaseSettings, SecretStr


class Settings(BaseSettings):
    """Settings that are loaded from the ``.env`` file."""

    BOT_TOKEN: SecretStr
    BACKEND_URL: AnyHttpUrl
    HTTP_TIMEOUT: float = 10.0

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

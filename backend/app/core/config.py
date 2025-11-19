import os

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

load_dotenv()


class Settings(BaseModel):
    PROJECT_NAME: str = "RPG Life API"
    API_V1_STR: str = "/api/v1"

    MODE: str = "debug"  # debug или prod
    SQLALCHEMY_DATABASE_URI: str | None = None

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1/chat/completions"

    model_config = ConfigDict(arbitrary_types_allowed=True)


def _env_values() -> dict[str, str]:
    available = {}
    for field in Settings.model_fields:
        if field in os.environ:
            available[field] = os.environ[field]
    return available


settings = Settings(**_env_values())

if not settings.SQLALCHEMY_DATABASE_URI:
    if settings.MODE == "debug":
        settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./debug.db"
    else:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI must be provided in prod mode")

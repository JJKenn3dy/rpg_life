from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RPG Life API"
    API_V1_STR: str = "/api/v1"

    MODE: str = "debug"  # debug или prod
    SQLALCHEMY_DATABASE_URI: str | None = None

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1/chat/completions"

    class Config:
        env_file = ".env"

settings = Settings()

# если строка подключения не задана, а режим debug – включаем SQLite
if not settings.SQLALCHEMY_DATABASE_URI:
    if settings.MODE == "debug":
        settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./debug.db"
    else:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI must be provided in prod mode")

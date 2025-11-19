from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=(settings.MODE == "debug"),  # в debug видно SQL-запросы
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

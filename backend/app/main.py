from fastapi import FastAPI
from backend.app.db.session import engine
from backend.app.db.base import Base

# импорт моделей, чтобы SQLAlchemy видел их перед create_all
from backend.app.models import user
from backend.app.models import domain   # или domains — как у тебя называется

app = FastAPI()

Base.metadata.create_all(bind=engine)

from backend.app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")

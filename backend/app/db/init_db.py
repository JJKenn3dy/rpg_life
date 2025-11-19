from app.db.base import Base
from app.db.session import engine

# важно импортнуть модели, чтобы таблицы создались
import app.models.user

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()

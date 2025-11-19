from sqlalchemy import Column, Integer, ForeignKey
from backend.app.db.base import Base

class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"))

    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    xp_needed = Column(Integer, default=100)

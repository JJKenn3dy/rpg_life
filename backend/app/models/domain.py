from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.base import Base


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String, nullable=False, index=True)

    current_level = Column(Integer, default=1)
    current_xp = Column(Integer, default=0)
    xp_to_next_level = Column(Integer, default=100)

    last_updated_at = Column(DateTime, default=datetime.utcnow)
    progress_in_level = Column(Float, default=0.0)

    user = relationship("User", back_populates="domains")

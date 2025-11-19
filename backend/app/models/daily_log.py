from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"
    __table_args__ = (
        Index("ix_daily_logs_user_date", "user_id", "log_date"),
        UniqueConstraint("user_id", "log_date", name="uq_daily_logs_user_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_score = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    summary = Column(String(280), nullable=True)
    xp_pulse_sent = Column(Boolean, default=False)
    xp_pulse_received = Column(Boolean, default=False)
    xp_pulse = Column(Boolean, default=False, nullable=False)
    self_rating = Column(Integer, nullable=False)
    log_date = Column(Date, nullable=False)
    streak_length = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="daily_logs")

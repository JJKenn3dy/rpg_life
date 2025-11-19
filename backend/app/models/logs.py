from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    log_date = Column(Date, default=date.today, nullable=False)

    summary = Column(Text, nullable=True)
    accomplishments = Column(Text, nullable=True)
    blockers = Column(Text, nullable=True)

    rating = Column(Integer, default=0)
    xp_pulse = Column(Boolean, default=False)
    total_xp_awarded = Column(Integer, default=0)
    xp_breakdown = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="daily_logs")
    finances = relationship("IncomeEntry", back_populates="daily_log", cascade="all, delete-orphan")


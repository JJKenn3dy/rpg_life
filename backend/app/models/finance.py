from __future__ import annotations

from datetime import date

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class IncomeEntry(Base):
    __tablename__ = "income_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    daily_log_id = Column(Integer, ForeignKey("daily_logs.id"), nullable=True, index=True)

    amount = Column(Integer, nullable=False)
    source = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    received_at = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="income_entries")
    daily_log = relationship("DailyLog", back_populates="finances")


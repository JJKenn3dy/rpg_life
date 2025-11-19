from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    current_global_level = Column(Integer, default=1)
    global_xp = Column(Integer, default=0)

    domains = relationship("Domain", back_populates="user", cascade="all, delete-orphan")
    daily_logs = relationship("DailyLog", back_populates="user", cascade="all, delete-orphan")
    income_entries = relationship("IncomeEntry", back_populates="user", cascade="all, delete-orphan")
    weekly_logs = relationship("WeeklyLog", back_populates="user", cascade="all, delete-orphan")
    monthly_logs = relationship("MonthlyLog", back_populates="user", cascade="all, delete-orphan")
    yearly_logs = relationship("YearlyLog", back_populates="user", cascade="all, delete-orphan")


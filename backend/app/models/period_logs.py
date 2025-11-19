from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


class PeriodLogBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    log_count = Column(Integer, nullable=False, default=0)
    total_xp = Column(Integer, nullable=False, default=0)
    average_rating = Column(Float, nullable=False, default=0.0)
    xp_pulse_count = Column(Integer, nullable=False, default=0)
    total_income = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class WeeklyLog(PeriodLogBase):
    __tablename__ = "weekly_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "period_start", name="uq_weekly_logs_user_period"),
    )

    user = relationship("User", back_populates="weekly_logs")


class MonthlyLog(PeriodLogBase):
    __tablename__ = "monthly_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "period_start", name="uq_monthly_logs_user_period"),
    )

    user = relationship("User", back_populates="monthly_logs")


class YearlyLog(PeriodLogBase):
    __tablename__ = "yearly_logs"
    __table_args__ = (
        UniqueConstraint("user_id", "period_start", name="uq_yearly_logs_user_period"),
    )

    user = relationship("User", back_populates="yearly_logs")

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.deps import get_db
from backend.app.models.period_logs import MonthlyLog, WeeklyLog, YearlyLog
from backend.app.models.user import User
from backend.app.schemas.period_logs import (
    MonthlyLogRead,
    WeeklyLogRead,
    YearlyLogRead,
)
from backend.app.services.log_aggregator import LogAggregator

router = APIRouter()


def get_user(db: Session, tg_id: str) -> User:
    user = db.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


def _ensure_aggregated(db: Session, user: User) -> None:
    aggregator = LogAggregator(db)
    aggregator.aggregate_user(user.id)


@router.get("/weekly-logs", response_model=list[WeeklyLogRead])
def list_weekly_logs(
    tg_id: str,
    limit: int = 12,
    db: Session = Depends(get_db),
):
    user = get_user(db, tg_id)
    _ensure_aggregated(db, user)
    logs = (
        db.query(WeeklyLog)
        .filter(WeeklyLog.user_id == user.id)
        .order_by(WeeklyLog.period_start.desc())
        .limit(limit)
        .all()
    )
    return logs


@router.get("/monthly-logs", response_model=list[MonthlyLogRead])
def list_monthly_logs(
    tg_id: str,
    limit: int = 12,
    db: Session = Depends(get_db),
):
    user = get_user(db, tg_id)
    _ensure_aggregated(db, user)
    logs = (
        db.query(MonthlyLog)
        .filter(MonthlyLog.user_id == user.id)
        .order_by(MonthlyLog.period_start.desc())
        .limit(limit)
        .all()
    )
    return logs


@router.get("/yearly-logs", response_model=list[YearlyLogRead])
def list_yearly_logs(
    tg_id: str,
    limit: int = 5,
    db: Session = Depends(get_db),
):
    user = get_user(db, tg_id)
    _ensure_aggregated(db, user)
    logs = (
        db.query(YearlyLog)
        .filter(YearlyLog.user_id == user.id)
        .order_by(YearlyLog.period_start.desc())
        .limit(limit)
        .all()
    )
    return logs

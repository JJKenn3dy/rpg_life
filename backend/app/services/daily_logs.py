"""Business logic for working with daily logs."""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.app.models.daily_log import DailyLog
from backend.app.models.user import User
from backend.app.schemas.daily_log import DailyLogCreate


def _resolve_log_date(payload: DailyLogCreate) -> date:
    return payload.log_date or date.today()


def _calculate_streak_length(
    previous_log: DailyLog | None, log_date: date
) -> int:
    if not previous_log:
        return 1

    if previous_log.log_date == log_date - timedelta(days=1):
        return previous_log.streak_length + 1

    return 1


def _auto_self_rating(payload: DailyLogCreate) -> int:
    """Calculate a deterministic rating based on the payload fields."""

    normalized_score = max(0, min(payload.day_score, 100))
    base_rating = (normalized_score + 5) // 10  # round to closest 10

    bonus = int(payload.xp_pulse_sent) + int(payload.xp_pulse_received)
    if payload.xp_pulse:
        bonus += 1

    rating = base_rating + bonus
    return max(1, min(10, rating))


def create_daily_log(db: Session, user: User, payload: DailyLogCreate) -> DailyLog:
    log_date = _resolve_log_date(payload)

    previous_log = (
        db.query(DailyLog)
        .filter(DailyLog.user_id == user.id, DailyLog.log_date < log_date)
        .order_by(DailyLog.log_date.desc())
        .first()
    )

    streak_length = _calculate_streak_length(previous_log, log_date)
    self_rating = payload.self_rating
    if self_rating is None:
        self_rating = _auto_self_rating(payload)

    log = DailyLog(
        user_id=user.id,
        day_score=payload.day_score,
        notes=payload.notes,
        summary=payload.summary,
        xp_pulse_sent=payload.xp_pulse_sent,
        xp_pulse_received=payload.xp_pulse_received,
        xp_pulse=payload.xp_pulse,
        self_rating=self_rating,
        log_date=log_date,
        streak_length=streak_length,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

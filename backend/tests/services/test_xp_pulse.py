"""Tests for streak calculations when saving daily logs."""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.daily_log import DailyLogCreate
from backend.app.services.daily_logs import create_daily_log


def test_streak_growth_and_reset(db_session: Session):
    user = User(tg_id="tg-service", username="tester")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    base_date = date(2024, 3, 1)

    first = create_daily_log(
        db=db_session,
        user=user,
        payload=DailyLogCreate(day_score=5, log_date=base_date, xp_pulse=True),
    )
    assert first.streak_length == 1

    second = create_daily_log(
        db=db_session,
        user=user,
        payload=DailyLogCreate(
            day_score=7,
            log_date=base_date + timedelta(days=1),
            xp_pulse=False,
        ),
    )
    assert second.streak_length == 2

    skipped_day = base_date + timedelta(days=3)
    third = create_daily_log(
        db=db_session,
        user=user,
        payload=DailyLogCreate(day_score=6, log_date=skipped_day, xp_pulse=True),
    )
    assert third.streak_length == 1

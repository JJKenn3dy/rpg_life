from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Tuple, TypeVar

from sqlalchemy.orm import Session, joinedload

from backend.app.models.logs import DailyLog
from backend.app.models.period_logs import MonthlyLog, WeeklyLog, YearlyLog

PeriodLogModel = TypeVar("PeriodLogModel", WeeklyLog, MonthlyLog, YearlyLog)


@dataclass
class AggregateBucket:
    log_count: int = 0
    total_xp: int = 0
    total_rating: int = 0
    xp_pulse_count: int = 0
    total_income: int = 0

    def feed(self, log: DailyLog) -> None:
        self.log_count += 1
        self.total_xp += log.total_xp_awarded or 0
        self.total_rating += log.rating or 0
        self.xp_pulse_count += 1 if log.xp_pulse else 0
        income = sum(entry.amount for entry in getattr(log, "finances", []) or [])
        self.total_income += income

    def finalize(self) -> dict:
        average = 0.0
        if self.log_count:
            average = round(self.total_rating / self.log_count, 2)
        return {
            "log_count": self.log_count,
            "total_xp": self.total_xp,
            "average_rating": average,
            "xp_pulse_count": self.xp_pulse_count,
            "total_income": self.total_income,
        }


class LogAggregator:
    def __init__(self, db: Session):
        self.db = db

    def aggregate_user(self, user_id: int) -> None:
        logs: Iterable[DailyLog] = (
            self.db.query(DailyLog)
            .filter(DailyLog.user_id == user_id)
            .options(joinedload(DailyLog.finances))
            .all()
        )
        if not logs:
            return

        weekly: dict[tuple[date, date], AggregateBucket] = defaultdict(AggregateBucket)
        monthly: dict[tuple[date, date], AggregateBucket] = defaultdict(AggregateBucket)
        yearly: dict[tuple[date, date], AggregateBucket] = defaultdict(AggregateBucket)

        for log in logs:
            week_key = _week_bounds(log.log_date)
            month_key = _month_bounds(log.log_date)
            year_key = _year_bounds(log.log_date)

            weekly[week_key].feed(log)
            monthly[month_key].feed(log)
            yearly[year_key].feed(log)

        modified = False
        modified |= self._persist_groups(user_id, WeeklyLog, weekly)
        modified |= self._persist_groups(user_id, MonthlyLog, monthly)
        modified |= self._persist_groups(user_id, YearlyLog, yearly)

        if modified:
            self.db.commit()

    def _persist_groups(self, user_id: int, model: type[PeriodLogModel], groups: dict) -> bool:
        changed = False
        for (start, end), bucket in groups.items():
            payload = bucket.finalize()
            instance = (
                self.db.query(model)
                .filter(model.user_id == user_id, model.period_start == start)
                .one_or_none()
            )
            if instance:
                instance.period_end = end
                for field, value in payload.items():
                    setattr(instance, field, value)
            else:
                instance = model(
                    user_id=user_id,
                    period_start=start,
                    period_end=end,
                    **payload,
                )
                self.db.add(instance)
            changed = True
        if changed:
            self.db.flush()
        return changed


def _week_bounds(current: date) -> Tuple[date, date]:
    start = current - timedelta(days=current.weekday())
    end = start + timedelta(days=6)
    return start, end


def _month_bounds(current: date) -> Tuple[date, date]:
    start = current.replace(day=1)
    if current.month == 12:
        next_month = current.replace(year=current.year + 1, month=1, day=1)
    else:
        next_month = current.replace(month=current.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return start, end


def _year_bounds(current: date) -> Tuple[date, date]:
    start = current.replace(month=1, day=1)
    end = current.replace(month=12, day=31)
    return start, end

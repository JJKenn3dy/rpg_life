from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class PeriodLogRead(BaseModel):
    id: int
    period_start: date
    period_end: date
    log_count: int
    total_xp: int
    average_rating: float
    xp_pulse_count: int
    total_income: int

    model_config = ConfigDict(from_attributes=True)


class WeeklyLogRead(PeriodLogRead):
    ...


class MonthlyLogRead(PeriodLogRead):
    ...


class YearlyLogRead(PeriodLogRead):
    ...

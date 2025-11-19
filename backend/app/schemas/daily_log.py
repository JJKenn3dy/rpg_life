from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DailyLogBase(BaseModel):
    day_score: int
    notes: str | None = None
    xp_pulse_sent: bool = False
    xp_pulse_received: bool = False
    xp_pulse: bool = False


class DailyLogCreate(DailyLogBase):
    log_date: date | None = None


class DailyLogRead(DailyLogBase):
    id: int
    user_id: int
    log_date: date
    streak_length: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

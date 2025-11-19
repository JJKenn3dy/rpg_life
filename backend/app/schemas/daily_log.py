from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DailyLogBase(BaseModel):
    day_score: int
    notes: str | None = None
    xp_pulse_sent: bool = False
    xp_pulse_received: bool = False


class DailyLogCreate(DailyLogBase):
    pass


class DailyLogRead(DailyLogBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

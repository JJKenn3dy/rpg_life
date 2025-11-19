from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.app.schemas.finance import IncomeRead, IncomeInput


class DomainXPUpdate(BaseModel):
    domain_id: int
    xp: int = Field(gt=0)


class DailyLogCreate(BaseModel):
    log_date: Optional[date] = None
    summary: Optional[str] = None
    accomplishments: Optional[str] = None
    blockers: Optional[str] = None
    rating: int = Field(ge=0, le=10)
    xp_pulse: Optional[bool] = None
    xp_updates: List[DomainXPUpdate] = Field(default_factory=list)
    finances: List[IncomeInput] = Field(default_factory=list)


class DailyLogRead(BaseModel):
    id: int
    log_date: date
    summary: Optional[str]
    accomplishments: Optional[str]
    blockers: Optional[str]
    rating: int
    xp_pulse: bool
    total_xp_awarded: int
    xp_breakdown: list[dict]
    finances: List[IncomeRead]

    model_config = ConfigDict(from_attributes=True)


from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class IncomeInput(BaseModel):
    amount: int = Field(gt=0)
    source: str
    description: Optional[str] = None
    received_at: Optional[date] = None


class IncomeCreate(IncomeInput):
    daily_log_id: Optional[int] = None


class IncomeRead(BaseModel):
    id: int
    amount: int
    source: str
    description: Optional[str]
    received_at: date
    daily_log_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)


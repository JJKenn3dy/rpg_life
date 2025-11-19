from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    tg_id: str
    username: Optional[str] = None

class UserRead(BaseModel):
    id: int
    tg_id: str
    username: Optional[str]
    registered_at: Optional[datetime]
    current_global_level: int
    global_xp: int

    model_config = ConfigDict(from_attributes=True)

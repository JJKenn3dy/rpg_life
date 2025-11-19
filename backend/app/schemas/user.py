from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    tg_id: str
    username: Optional[str] = None

class UserRead(BaseModel):
    id: int
    tg_id: str
    username: Optional[str]
    current_global_level: int
    global_xp: int

    model_config = ConfigDict(from_attributes=True)

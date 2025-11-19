from pydantic import BaseModel, ConfigDict

class DomainCreate(BaseModel):
    name: str

class DomainRead(BaseModel):
    id: int
    name: str
    current_level: int
    current_xp: int
    xp_to_next_level: int

    model_config = ConfigDict(from_attributes=True)

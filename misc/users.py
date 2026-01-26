from pydantic import BaseModel, ConfigDict
from typing import List

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str

class UserList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    users: List[UserBase]
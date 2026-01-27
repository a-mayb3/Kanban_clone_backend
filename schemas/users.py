from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdateInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserUpdatePassword(BaseModel):
    password: str
    new_password: str


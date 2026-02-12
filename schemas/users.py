from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdateInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class UserUpdatePassword(BaseModel):
    password: str
    new_password: str

class UserLogin(BaseModel):
    email: str
    password: str

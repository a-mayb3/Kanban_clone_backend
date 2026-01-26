from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from tasks import TaskBase
from users import UserBase

class ProjectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: str
    tasks: List[TaskBase]
    users: List[UserBase]

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tasks: List[TaskBase] = []
    user_ids: List[int] = []

class ProjectList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    projects: List[ProjectBase]
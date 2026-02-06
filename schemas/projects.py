from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from schemas.tasks import TaskBase
from schemas.users import UserBase

class ProjectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    description: str
    tasks: List[TaskBase]
    users: List[UserBase]

class ProjectFull(ProjectBase):
    id: int

class ProjectCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    tasks: List[TaskBase] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectAddUsers(BaseModel):
    user_ids: List[int] = []

class ProjectRemoveUsers(BaseModel):
    user_ids: List[int] = []

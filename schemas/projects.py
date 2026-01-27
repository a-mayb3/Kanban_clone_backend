from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from schemas.tasks import TaskBase
from schemas.users import UserBase

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

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectAddUsers(BaseModel):
    user_ids: List[int] = []

class ProjectRemoveUsers(BaseModel):
    user_ids: List[int] = []

from typing import List

from pydantic import ConfigDict
from schemas.projects import ProjectBase
from schemas.users import UserBase

class ProjectUserBase(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    projects: List[ProjectBase]

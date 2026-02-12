import schemas.projects as project_schemas
import schemas.tasks as task_schemas
from pydantic import ConfigDict

class ProjectTaskBase(task_schemas.TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    project: project_schemas.ProjectBase

class ProjectTaskCreate(task_schemas.TaskCreate):
    project: project_schemas.ProjectBase
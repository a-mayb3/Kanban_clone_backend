from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List, Annotated, Optional
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session, joinedload

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    STASHED = "stashed"

class TaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING

class TaskList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    tasks: List[TaskBase]

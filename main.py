from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated

app = FastAPI()

class TaskStatus():
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    STASHED = "stashed"

class TaskBase(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus

class ProjectBase(BaseModel):
    id: int
    name: str
    description: str
    tasks: List[TaskBase]

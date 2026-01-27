from typing import List
from schemas.tasks import TaskBase
from fastapi import APIRouter, HTTPException, Depends

from database import db_dependency

import models

router = APIRouter(prefix="/tasks", tags=["tasks"])

# """Get tasks from a specified project"""
# @router.get("/from_project/{project_id}", response_model=List[TaskBase])
# def read_tasks_from_project(project_id: int, db: db_dependency):
#     db_tasks = db.query(models.Task).filter(models.Task.project_id == project_id).all()
#     return db_tasks


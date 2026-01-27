from fastapi import APIRouter, HTTPException, Depends
from typing import List, Annotated

from database import db_dependency

import schemas.tasks as tasks
import schemas.projects as projects

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/{project_id}", response_model=projects.ProjectBase)
def read_project(project_id: int, db: db_dependency):
    db_project = db.query(projects.models.Project).filter(projects.models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.get("/{project_id}/tasks", response_model=List[tasks.TaskBase])
def read_tasks_from_project(project_id: int, db: db_dependency):
    db_tasks = db.query(tasks.models.Task).filter(tasks.models.Task.project_id == project_id).all()
    return db_tasks

@router.get("/{project_id}/tasks/{task_id}", response_model=tasks.TaskBase)
def read_task_from_project(project_id: int, task_id: int, db: db_dependency):
    db_task = db.query(tasks.models.Task).filter(tasks.models.Task.project_id == project_id, tasks.models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found in the specified project")
    return db_task

@router.post("/", response_model=projects.ProjectCreate)
def create_project(project: projects.ProjectCreate, db: db_dependency):
    db_project = projects.models.Project(
        name=project.name,
        description=project.description
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.post("/{project_id}/tasks", response_model=tasks.TaskBase)
def create_task_in_project(project_id: int, task: tasks.TaskBase, db: db_dependency):
    db_task = tasks.models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        project_id=project_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
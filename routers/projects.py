from fastapi import APIRouter, HTTPException, Depends
from typing import List, Annotated

from database import db_dependency

import schemas.tasks as tasks
import schemas.projects as projects
import schemas.users as users

router = APIRouter(prefix="/projects", tags=["projects"])

##
## GET endpoints
##


"""Get a project by ID"""

@router.get("/{project_id}", response_model=projects.ProjectBase)
def read_project(project_id: int, db: db_dependency):
    db_project = db.query(projects.models.Project).filter(projects.models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

"""Get tasks from a specified project"""
@router.get("/{project_id}/tasks", response_model=List[tasks.TaskBase], tags=["tasks"])
def read_tasks_from_project(project_id: int, db: db_dependency):
    db_tasks = db.query(tasks.models.Task).filter(tasks.models.Task.project_id == project_id).all()
    return db_tasks

"""Get a specific task from a specified project"""
@router.get("/{project_id}/tasks/{task_id}", response_model=tasks.TaskBase, tags=["tasks"])
def read_task_from_project(project_id: int, task_id: int, db: db_dependency):
    db_task = db.query(tasks.models.Task).filter(tasks.models.Task.project_id == project_id, tasks.models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found in the specified project")
    return db_task


"""Get users from a specified project"""

@router.get("/{project_id}/users", response_model=List[users.UserBase], tags=["users"])
def read_users_from_project(project_id: int, db: db_dependency):
    db_project = db.query(projects.models.Project).filter(projects.models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project.users


##
## POST endpoints
##


"""Create a new project"""

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


"""Create a new task in a specified project"""

@router.post("/{project_id}/tasks", response_model=tasks.TaskBase, tags=["tasks"])
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


"""Add users to a specified project using their IDs"""

@router.post("/{project_id}/users", response_model=projects.ProjectAddUsers, tags=["users"])
def add_users_to_project(project_id: int, user_data: projects.ProjectAddUsers, db: db_dependency):
    db_project = db.query(projects.models.Project).filter(projects.models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for user_id in user_data.user_ids:
        db_user = db.query(users.models.User).filter(users.models.User.id == user_id).first()
        if db_user:
            db_project.users.append(db_user)
    db.commit()
    db.refresh(db_project)
    return db_project


##
## PUT endpoints
##


"""Update a project by ID"""

@router.put("/{project_id}", response_model=projects.ProjectUpdate)
def update_project(project_id: int, project: projects.ProjectUpdate, db: db_dependency):
    db_project = db.query(projects.models.Project).filter(projects.models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.name is not None:
        db_project.name = project.name
    if project.description is not None:
        db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    return db_project


"""Update a task in a specified project"""

@router.put("/{project_id}/tasks/{task_id}", response_model=tasks.TaskUpdate, tags=["tasks"])
def update_task_in_project(project_id: int, task_id: int, task: tasks.TaskUpdate, db: db_dependency):
    db_task = db.query(tasks.models.Task).filter(tasks.models.Task.project_id == project_id, tasks.models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found in the specified project")
    if task.title is not None:
        db_task.title = task.title
    if task.description is not None:
        db_task.description = task.description
    if task.status is not None:
        db_task.status = task.status
    db.commit()
    db.refresh(db_task)
    return db_task

##
## DELETE endpoints
##

"""Delete a project by ID"""

@router.delete("/{project_id}")
def delete_project(project_id: int, db: db_dependency):
    db_project = db.query(projects.models.Project).filter(projects.models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"detail": "Project deleted successfully"}


"""Delete a task from a specified project"""

@router.delete("/{project_id}/tasks/{task_id}" , tags=["tasks"])
def delete_task_from_project(project_id: int, task_id: int, db: db_dependency):
    db_task = db.query(tasks.models.Task).filter(tasks.models.Task.project_id == project_id, tasks.models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found in the specified project")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted successfully"}


"""Remove users from a specified project using their IDs"""

@router.delete("/{project_id}/users/{user_id}", tags=["users"])
def remove_user_from_project(project_id: int, user_id: int, db: db_dependency):
    db_project = db.query(projects.models.Project).filter(projects.models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db_user = db.query(users.models.User).filter(users.models.User.id == user_id).first()
    if db_user is None or db_user not in db_project.users:
        raise HTTPException(status_code=404, detail="User not found in the specified project")
    db_project.users.remove(db_user)
    db.commit()
    db.refresh(db_project)
    return {"detail": "User removed from project successfully"}

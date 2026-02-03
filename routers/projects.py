from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Annotated

from database import db_dependency

import schemas.tasks as tasks_schemas
import schemas.projects as projects_schemas
import schemas.users as users_schemas
import schemas.projects_tasks as projects_tasks_schemas

from models import Project
from routers.auth import get_user_from_jwt

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[projects_schemas.ProjectBase], tags=["projects", "me"])
def get_projects(db: db_dependency, request: Request):
    """Get a user's projects"""

    user = get_user_from_jwt(request, db)
    user_id = getattr(user, "id")

    ## fetching projects for the user
    projects = db.query(Project).join(Project.users).filter(getattr(users_schemas.UserBase, "id") == int(user_id)).all()
    return projects


@router.get("/{project_id}", response_model=projects_schemas.ProjectBase)
def get_project(project_id: int, request:Request, db: db_dependency):
    """Get a project by ID"""
    
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    return db_project

@router.get("/{project_id}/users", response_model=List[users_schemas.UserBase], tags=["users", "projects"])
def get_project_users(project_id: int, request:Request, db: db_dependency):
    """Get users from a specified project"""
    
    user = get_user_from_jwt(request, db)
    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project's users")
    
    return db_project.users

@router.get("/{project_id}/tasks", response_model=List[tasks_schemas.TaskBase], tags=["tasks", "projects"])
def get_project_tasks(project_id: int, request:Request, db: db_dependency):
    """Get tasks from a specified project"""
    
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project's tasks")
    
    return db.query(tasks_schemas.TaskBase).filter(getattr(tasks_schemas.TaskBase, "project_id") == project_id).all()

@router.post("/", response_model=projects_schemas.ProjectCreate)
def create_project(project: projects_schemas.ProjectCreate, request:Request, db: db_dependency):
    """Create a new project"""
    
    user = get_user_from_jwt(request, db)
    db_project = projects_schemas.ProjectCreate(
        name=project.name,
        description=project.description,
        tasks=[],
        user_ids=[getattr(user, "id")]
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    db.commit()
    db.refresh(db_project)
    
    return db_project

@router.get("/{project_id}/tasks/{task_id}", response_model=tasks_schemas.TaskBase, tags=["tasks"])
def read_task_from_project(project_id: int, task_id: int, db: db_dependency, request: Request):
    """Get a specific task from a specified project"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project's tasks")

    db_task = db.query(tasks_schemas.TaskBase).filter(getattr(tasks_schemas.TaskBase, "project_id") == project_id, getattr(tasks_schemas.TaskBase, "id") == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found in the specified project")
    return db_task

@router.get("/{project_id}/users/{user_id}", response_model=users_schemas.UserBase, tags=["users"])
def read_user_from_project(project_id: int, user_id: int, db: db_dependency, request: Request):
    """Get a specific user from a specified project"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project's users")

    db_user = db.query(users_schemas.UserBase).filter(getattr(users_schemas.UserBase, "id") == user_id).first()
    if db_user is None or db_user not in db_project.users:
        raise HTTPException(status_code=404, detail="User not found in the specified project")
    return db_user

@router.post("/{project_id}/tasks", response_model=projects_tasks_schemas.ProjectTaskCreate, tags=["tasks"])
def create_task_in_project(project_id: int, task: tasks_schemas.TaskCreate, db: db_dependency, request: Request):
    """Create a new task in a specified project"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to add tasks to this project")

    db_task = projects_tasks_schemas.ProjectTaskCreate(
        title=task.title,
        description=task.description,
        status=task.status,
        project=db_project
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.post("/{project_id}/users", response_model=projects_schemas.ProjectAddUsers, tags=["users"])
def add_users_to_project(project_id: int, user_data: projects_schemas.ProjectAddUsers, db: db_dependency, request: Request):
    """Add users to a specified project using their IDs"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project's users")

    for user_id in user_data.user_ids:
        db_user = db.query(users_schemas.UserBase).filter(getattr(users_schemas.UserBase, "id") == user_id).first()
        if db_user:
            db_project.users.append(db_user)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}/users/{user_id}", response_model=projects_schemas.ProjectRemoveUsers, tags=["users"])
def remove_user_from_project(project_id: int, user_id: int, db: db_dependency, request: Request):
    """Remove a user from a specified project using their ID"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project's users")

    db_user = db.query(users_schemas.UserBase).filter(getattr(users_schemas.UserBase, "id") == user_id).first()
    if db_user is None or db_user not in db_project.users:
        raise HTTPException(status_code=404, detail="User not found in the specified project")

    db_project.users.remove(db_user)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/{project_id}/tasks/{task_id}", response_model=tasks_schemas.TaskUpdate, tags=["tasks"])
def update_task_in_project(project_id: int, task_id: int, task: tasks_schemas.TaskUpdate, db: db_dependency, request: Request):
    """Update a task in a specified project"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project's tasks")

    db_task = db.query(tasks_schemas.TaskBase).filter(getattr(tasks_schemas.TaskBase, "project_id") == project_id, getattr(tasks_schemas.TaskBase, "id") == task_id).first()
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

@router.put("/{project_id}", response_model=projects_schemas.ProjectUpdate)
def update_project(project_id: int, project: projects_schemas.ProjectUpdate, db: db_dependency, request: Request):
    """Update a project by ID"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")
    if project.name is not None:
        db_project.name = project.name
    if project.description is not None:
        db_project.description = project.description
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}", tags=["projects"])
def delete_project(project_id: int, db: db_dependency, request: Request):
    """Delete a project by ID"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    db.delete(db_project)
    db.commit()
    return {"detail": "Project deleted successfully"}

@router.delete("/{project_id}/tasks/{task_id}" , tags=["tasks"])
def delete_task_from_project(project_id: int, task_id: int, db: db_dependency, request: Request):
    """Delete a task from a specified project"""
    user = get_user_from_jwt(request, db)

    db_project = db.query(projects_schemas.ProjectBase).filter(getattr(projects_schemas.ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if  user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project's tasks")

    db_task = db.query(tasks_schemas.TaskBase).filter(getattr(tasks_schemas.TaskBase, "project_id") == project_id, getattr(tasks_schemas.TaskBase, "id") == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found in the specified project")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted successfully"}

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Annotated

from database import db_dependency

from schemas.tasks import TaskBase, TaskCreate, TaskUpdate
from schemas.projects import ProjectBase, ProjectCreate, ProjectUpdate, ProjectAddUsers, ProjectRemoveUsers
from schemas.users import UserBase
from schemas.projects_users import ProjectUserBase
from schemas.projects_tasks import ProjectTaskBase, ProjectTaskCreate

from models import Project
from routers.auth import get_user_from_jwt
   
def get_project_by_id_for_user(user: UserBase, project_id: int, db: db_dependency) -> ProjectBase:
    """Get a project by ID and verify user has access"""
    db_project = db.query(ProjectBase).filter(getattr(ProjectBase, "id") == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if user not in db_project.users:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    return db_project

def get_task_by_id_for_project(project: ProjectBase, task_id: int, db: db_dependency) -> TaskBase:
    """
    Get a task by ID within a project
    Supposes the user has already been verified to have access to the project
    """
    db_task = db.query(TaskBase).filter(getattr(TaskBase, "id") == task_id, getattr(TaskBase, "project_id") == getattr(project, "id")).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found in the specified project")
    return db_task

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectBase], tags=["projects", "me"])
def get_projects(db: db_dependency, request: Request):
    """Get a user's projects"""

    user = get_user_from_jwt(request, db)
    user_id = getattr(user, "id")

    ## fetching projects for the user
    projects = db.query(Project).join(Project.users).filter(getattr(UserBase, "id") == int(user_id)).all()
    return projects


@router.get("/{project_id}", response_model=ProjectBase)
def get_project(project_id: int, request:Request, db: db_dependency):
    """Get a project by ID"""
    
    user = get_user_from_jwt(request, db)
    return get_project_by_id_for_user(user, project_id, db)

@router.get("/{project_id}/users", response_model=List[UserBase], tags=["users", "projects"])
def get_project_users(project_id: int, request:Request, db: db_dependency):
    """Get users from a specified project"""
    
    user = get_user_from_jwt(request, db)
    db_project = get_project_by_id_for_user(user, project_id, db)
    return db_project.users


@router.get("/{project_id}/tasks/{task_id}", response_model=TaskBase, tags=["tasks"])
def get_project_task(project_id: int, task_id: int, db: db_dependency, request: Request):
    """Get a specific task from a specified project"""
    
    user = get_user_from_jwt(request, db)
    db_project = get_project_by_id_for_user(user, project_id, db)
    db_task = get_task_by_id_for_project(db_project, task_id, db)

    return db_task

@router.get("/{project_id}/users/{user_id}", response_model=UserBase, tags=["users"])
def get_project_user(project_id: int, user_id: int, db: db_dependency, request: Request):
    """Get a specific user from a specified project"""
    user = get_user_from_jwt(request, db)

    db_project : ProjectBase = get_project_by_id_for_user(user, project_id, db)

    db_user = db.query(UserBase).filter(getattr(UserBase, "id") == user_id).first()
    if db_user is None or db_user not in db_project.users:
        raise HTTPException(status_code=404, detail="User not found in the specified project")
    return db_user

@router.get("/{project_id}/tasks", response_model=List[TaskBase], tags=["tasks", "projects"])
def get_project_tasks(project_id: int, request:Request, db: db_dependency):
    """Get tasks from a specified project"""
    
    user = get_user_from_jwt(request, db)
    db_project = get_project_by_id_for_user(user, project_id, db)
    db_tasks = db.query(TaskBase).filter(getattr(TaskBase, "project_id") == project_id).all()
    return db_tasks

@router.post("/", response_model=ProjectCreate)
def create_project(project: ProjectCreate, request:Request, db: db_dependency):
    """Create a new project"""
    
    user = get_user_from_jwt(request, db)

    db_project = ProjectCreate(
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


@router.post("/{project_id}/tasks", response_model=ProjectTaskCreate, tags=["tasks"])
def create_project_task(project_id: int, task: TaskCreate, db: db_dependency, request: Request):
    """Create a new task in a specified project"""
    user = get_user_from_jwt(request, db)

    db_project = get_project_by_id_for_user(user, project_id, db)

    db_task = ProjectTaskCreate(
        title=task.title,
        description=task.description,
        status=task.status,
        project=db_project
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.post("/{project_id}/users", response_model=ProjectAddUsers, tags=["users"])
def add_project_user(project_id: int, user_data: ProjectAddUsers, db: db_dependency, request: Request):
    """Add users to a specified project using their IDs"""
    user = get_user_from_jwt(request, db)

    db_project = get_project_by_id_for_user(user, project_id, db)

    for user_id in user_data.user_ids:
        db_user = db.query(UserBase).filter(getattr(UserBase, "id") == user_id).first()
        if db_user:
            db_project.users.append(db_user)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}/users/{user_id}", response_model=ProjectRemoveUsers, tags=["users"])
def remove_user_from_project(project_id: int, user_id: int, db: db_dependency, request: Request):
    """Remove a user from a specified project using their ID"""
    user = get_user_from_jwt(request, db)

    db_project = get_project_by_id_for_user(user, project_id, db)

    db_user = db.query(UserBase).filter(getattr(UserBase, "id") == user_id).first()
    if db_user is None or db_user not in db_project.users:
        raise HTTPException(status_code=404, detail="User not found in the specified project")

    db_project.users.remove(db_user)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/{project_id}/tasks/{task_id}", response_model=TaskUpdate, tags=["tasks"])
def update_project_task(project_id: int, task_id: int, task: TaskUpdate, db: db_dependency, request: Request):
    """Update a task in a specified project"""
    user = get_user_from_jwt(request, db)
    db_project = get_project_by_id_for_user(user, project_id, db)
    db_task = get_task_by_id_for_project(db_project, task_id, db)

    if task.title is not None:
        db_task.title = task.title
    if task.description is not None:
        db_task.description = task.description
    if task.status is not None:
        db_task.status = task.status

    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{project_id}", response_model=ProjectUpdate)
def update_project(project_id: int, project: ProjectUpdate, db: db_dependency, request: Request):
    """Update a project by ID"""
    user = get_user_from_jwt(request, db)

    db_project = get_project_by_id_for_user(user, project_id, db)

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
    db_project = get_project_by_id_for_user(user, project_id, db)
    
    db.delete(db_project)
    db.commit()
    return {"detail": "Project deleted successfully"}

@router.delete("/{project_id}/tasks/{task_id}" , tags=["tasks"])
def delete_project_task(project_id: int, task_id: int, db: db_dependency, request: Request):
    """Delete a task from a specified project"""
    user = get_user_from_jwt(request, db)
    db_project = get_project_by_id_for_user(user, project_id, db)
    db_task = get_task_by_id_for_project(db_project, task_id, db)
    
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted successfully"}

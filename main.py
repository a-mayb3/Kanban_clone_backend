from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import List, Annotated, Optional

import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session, joinedload

from misc.tasks import TaskBase, TaskList
from misc.users import UserBase
from misc.projects import ProjectBase, ProjectCreate, ProjectList

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/projects/", response_model=ProjectBase)
def create_project(project: ProjectCreate, db: db_dependency):
    db_project = models.Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    for task in project.tasks:
        db_task = models.Task(
            title=task.title,
            description=task.description,
            status=task.status.value,
            project_id=db_project.id
        )
        db.add(db_task)
    db.commit()

    if project.user_ids:
        users = db.query(models.User).filter(models.User.id.in_(project.user_ids)).all()
        db_project.users.extend(users)
        db.commit()

    db_project = db.query(models.Project).options(
        joinedload(models.Project.tasks),
        joinedload(models.Project.users)
    ).filter(models.Project.id == db_project.id).first()
    
    return db_project

@app.get("/projects/{project_id}", response_model=ProjectBase)
def read_project(project_id: int, db: db_dependency):
    db_project = db.query(models.Project).options(
        joinedload(models.Project.tasks),
        joinedload(models.Project.users)
    ).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project



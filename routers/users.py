from typing import List
from fastapi import APIRouter, HTTPException, Depends
from database import db_dependency

import models

import schemas.users as users
import schemas.projects as projects

router = APIRouter(prefix="/users", tags=["users"])



"""Get a user by ID"""

@router.get("/{user_id}", response_model=users.UserBase)
def read_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


"""Update a user by ID"""

@router.put("/{user_id}", response_model=users.UserBase)
def update_user(user_id: int, user: users.UserBase, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user


"""Get projects assigned to a user"""

@router.get("/{user_id}/projects", response_model=List[projects.ProjectBase])
def read_projects_from_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.projects

##
## POST endpoints
##


"""Create a new user"""

@router.post("/", response_model=users.UserBase)
def create_user(user: users.UserBase, db: db_dependency):
    db_user = models.User(
        name=user.name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
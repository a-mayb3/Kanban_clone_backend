import os
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request
from jose import JWTError, jwt
from database import db_dependency

import models

from routers import auth
import schemas.users as users
import schemas.projects as projects

from pyargon2 import hash

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=users.UserBase)
def read_user(user_id: int, db: db_dependency, request:Request):
    """Get a user by ID"""

    check_for_valid_token(request, db)
    
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/{user_id}/projects", response_model=List[projects.ProjectBase])
def read_projects_from_user(user_id: int, db: db_dependency, request: Request):
    """Get projects assigned to a user"""

    check_for_valid_token(request, db)

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.projects

##
## POST endpoints
##

@router.post("/", response_model=users.UserBase)
def create_user(user: users.UserCreate, db: db_dependency):
    """Create a new user"""

    user_salt = os.urandom(32).hex()
    print("Generated salt:", user_salt)
    
    hashed_password = hash(password=user.password, salt=user_salt, variant="id")
    
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        password_salt=user_salt
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}


def check_for_valid_token(request: Request, db: db_dependency) -> models.User :
    """Helper function to check for valid JWT token in cookies"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not logged in"
        )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: str = str(payload.get("sub"))
        if user_id is None:
            request.cookies.clear() ## removing invalid auth cookie
            raise HTTPException(
                status_code=401,
                detail="Not logged in"
            )
        db_user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if db_user is None:
            request.cookies.clear() ## removing invalid auth cookie
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        return db_user
    
    except JWTError:
        request.cookies.clear() ## removing invalid auth cookie
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )



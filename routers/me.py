from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from database import db_dependency
from jose import JWTError, jwt
import models

from routers import auth

from schemas.users import UserBase
from schemas.projects import ProjectBase
from schemas.projects_users import ProjectUserBase


router = APIRouter(prefix="/me", tags=["me"])

@router.get("/", response_model=ProjectUserBase, tags=["me", "users"])
def get_me(request: Request, db: db_dependency):
    """Get current authenticated user"""
    user = auth.get_user_from_jwt(request, db)
    return user


@router.get("/logout", tags=["me", "auth"])
def logout(request: Request,response: Response):
    """Logout by clearing the JWT cookie"""
    
    get_token = request.cookies.get("access_token")
    if not get_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in"
        )
    
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}

@router.delete("/delete-me", tags=["me", "auth", "users"])
def delete_me(request: Request, db: db_dependency):
    """Delete current authenticated user"""
    
    user = auth.get_user_from_jwt(request, db)

    ## Remove user from all projects, delete projects with no users left
    projects = user.projects[:]
    for project in projects:
        project.users.remove(user)
        if len(project.users) == 0:
            ## delete project if no users left
            tasks = project.tasks[:]
            for task in tasks:
                db.delete(task)
            db.delete(project)

    db.delete(user)
    db.commit()
    ## Logout user by clearing cookie
    request.cookies.clear()
    return {"message": "User deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from database import db_dependency
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import models
import os

from routers import auth
import schemas.users as user_schemas
import routers.users as user_router

router = APIRouter(prefix="/me", tags=["me"])

@router.get("/", response_model=user_schemas.UserBase)
def get_me(request: Request, db: db_dependency):
    """Get current authenticated user"""
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in"
        )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: str = str(payload.get("sub"))
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not logged in"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    db_user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return db_user
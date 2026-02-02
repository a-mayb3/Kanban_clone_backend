import os

from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from database import db_dependency
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import models

import schemas.users as user_schemas
import routers.users as user_router

from pyargon2 import hash

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.update({"iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login")
def login(user_data: user_schemas.UserLogin, request: Request, response: Response, db: db_dependency):
    """Login and receive JWT token in cookie"""

    ## check if access token already exists
    get_token = request.cookies.get("access_token")
    if get_token:
        try:
            user_id = verify_jwt_token(get_token)
            return {
                "message": "Already logged in",
                "user": {
                    "id": user_id
                }
            }
        except HTTPException:
            pass  # Token invalid or expired, proceed to login

    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_user_password(getattr(db_user, "id"), user_data.password, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    
    )
    
    # Set JWT in httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email
        }
    }

@router.post("/logout")
def logout(response: Response):
    """Logout by clearing the JWT cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}

def verify_jwt_token(token: str):
    """Verify and decode a JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception

def verify_user_password(user_id: int, password: str, db: db_dependency) -> bool:
    """Verify user's password"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return False
    
    hashed_password = hash(password=password, salt=str(getattr(db_user,"password_salt")), variant="id")
    if hashed_password != db_user.password_hash:
        return False

    return True
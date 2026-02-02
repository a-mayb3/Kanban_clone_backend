from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from database import db_dependency
from jose import JWTError, jwt
import models

from routers import auth
import schemas.users as user_schemas

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
            request.cookies.clear() ## removing invalid auth cookie
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not logged in"
            )
    except JWTError:
        request.cookies.clear() ## removing invalid auth cookie
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    db_user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if db_user is None:
        request.cookies.clear() ## removing invalid auth cookie
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return db_user


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
            request.cookies.clear() ## removing invalid auth cookie
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not logged in"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

## User retrieval and deletion
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        request.cookies.clear() ## removing invalid auth cookie
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    ## Logout user by clearing cookie
    request.cookies.clear()
    return {"message": "User deleted successfully"}

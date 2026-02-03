import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers.projects import router as projects_router

from routers.users import router as users_router
from routers.auth import router as auth_router
from routers.me import router as me_router
from database import init_db

app_description = """
This API serves as the backend for a Kanban-style project management application.
It allows users to manage projects, tasks, and user assignments with proper authentication and authorization.

## Stack
- FastAPI
- SQLAlchemy
- SQLite

## Features
- User Authentication (JWT and Argon2 Password Hashing)
- Project Management (Create, Read, Update, Delete)
- Task Management within Projects
- User Assignments to Projects
- CORS Configuration for Frontend Integration

## Source Code
The source code for this API can be found on [GitHub](https://github.com/a-mayb3/Kanban_clone_backend) or [my forgejo instance](https://git.vollex.cc/a-mayb3/Kanban_clone_backend).
"""

global_logger = logging.getLogger()
global_logger.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    encoding='utf-8'
    )
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
global_logger.addHandler(handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = global_logger

    # Place for startup and shutdown events if needed in the future
    logger.info("Initializing database...")
    init_db()
    yield

app = FastAPI(
    lifespan=lifespan,
    license_info={"name": "AGPL-3.0-or-later", "url": "https://www.gnu.org/licenses/agpl-3.0.en.html"},
    description=app_description,
    title="Kanban Clone Backend API",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(me_router)
app.include_router(projects_router)

"""ping pong :)"""
@app.get("/ping")
def ping():
    return {"message": "pong"}

"""Gives project url"""
@app.get("/sources")
def source():
    return {"url": "https://github.com/a-mayb3/Kanban_clone_backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi.exceptions import RequestValidationError 
from fastapi.responses import JSONResponse 

@app.exception_handler(HTTPException) 
async def http_exception_handler(request, exc): 
    """Custom HTTP exception handler""" 
    
    logger = global_logger
    logger.error(f"HTTP error occurred: {exc.detail}")
    
    return JSONResponse( 
        status_code=exc.status_code, 
        content={ 
            "error": { 
                "message": exc.detail, 
                "type": "authentication_error" if exc.status_code == 401 else "authorization_error", 
                "status_code": exc.status_code 
             } 
          }, 
          headers=exc.headers 
      ) 

@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request, exc): 
    """Handle validation errors"""

    logger = global_logger
    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse( 
        status_code=422, 
        content={ 
            "error": { 
                "message": "Validation error", 
                "type": "validation_error", 
                "details": exc.errors() 
           } 
        } 
     )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all other exceptions"""

    logger = global_logger
    logger.error(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected error occurred.",
                "type": "internal_server_error",
                "details": str(exc)
            }
        }
    )
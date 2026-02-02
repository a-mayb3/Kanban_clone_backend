import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers.projects import router as projects_router

from routers.users import router as users_router
from routers.auth import router as auth_router
from routers.me import router as me_router
from database import init_db

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

app = FastAPI(lifespan=lifespan)

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

## TODO: Add root endpoint that gives basic info about the API
## TODO: Add more detailed error handling and logging
## TODO: Implement authentication and authorization mechanisms

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
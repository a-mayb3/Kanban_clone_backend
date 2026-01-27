from fastapi import FastAPI, HTTPException, Depends

from routers.projects import router as projects_router
from routers.users import router as users_router

app = FastAPI()

app.include_router(users_router)
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

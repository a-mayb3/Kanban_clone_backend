from fastapi import FastAPI, HTTPException, Depends

from routers.tasks import router as tasks_router
from routers.projects import router as projects_router

app = FastAPI()

app.include_router(tasks_router)
app.include_router(projects_router)


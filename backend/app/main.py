from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.routers import auth, applicant, admin, pages, instructor, facilitator
from app.routers import instructor_api, facilitator_api
import os

app = FastAPI(title=settings.PROJECT_NAME)

# Setup directories
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "static")
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(applicant.router, prefix="/api/applicant", tags=["applicant"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(instructor.router, prefix="/instructor", tags=["instructor"])
app.include_router(instructor_api.router, prefix="/api/instructor", tags=["instructor-api"])
app.include_router(facilitator.router, prefix="/facilitator", tags=["facilitator"])
app.include_router(facilitator_api.router, prefix="/api/facilitator", tags=["facilitator-api"])
app.include_router(pages.router, tags=["pages"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

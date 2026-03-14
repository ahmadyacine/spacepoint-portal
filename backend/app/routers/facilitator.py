from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from app.routers.deps import get_current_user
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
def dashboard(request: Request, facilitator: User = Depends(get_current_user)):
    return templates.TemplateResponse("facilitator/dashboard.html", {
        "request": request,
        "user": facilitator,
        "active_page": "dashboard"
    })

@router.get("/training")
def training(request: Request, facilitator: User = Depends(get_current_user)):
    return templates.TemplateResponse("facilitator/training.html", {
        "request": request,
        "user": facilitator,
        "active_page": "training"
    })

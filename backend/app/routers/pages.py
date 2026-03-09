from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from app.routers.deps import get_current_user

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@router.get("/apply", response_class=HTMLResponse)
def apply_page(request: Request):
    return templates.TemplateResponse("apply.html", {"request": request})

@router.get("/tasks/videos", response_class=HTMLResponse)
def videos_page(request: Request):
    return templates.TemplateResponse("videos.html", {"request": request})

@router.get("/tasks/modules", response_class=HTMLResponse)
def modules_dashboard_page(request: Request):
    return templates.TemplateResponse("modules.html", {"request": request})

@router.get("/tasks/modules/{module_id}", response_class=HTMLResponse)
def module_detail_page(request: Request, module_id: int):
    return templates.TemplateResponse("module_detail.html", {"request": request, "module_id": module_id})

@router.get("/status", response_class=HTMLResponse)
def status_page(request: Request):
    return templates.TemplateResponse("status.html", {"request": request})

@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

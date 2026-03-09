from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.routers.deps import get_current_user, get_db
from app.models.user import User, UserRole
from app.models.instructor_profile import InstructorProfile

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_current_instructor(user: User = Depends(get_current_user)):
    # Note: Using string "INSTRUCTOR" since UserRole string value is "INSTRUCTOR"
    if user.role != UserRole.INSTRUCTOR and user.role != "INSTRUCTOR":
        raise HTTPException(status_code=403, detail="Not authorized as instructor")
    return user

@router.get("/dashboard")
def dashboard(request: Request, instructor: User = Depends(get_current_instructor), db: Session = Depends(get_db)):
    # Force first-time password change
    if instructor.must_change_password:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/instructor/change-password", status_code=302)
    from app.models.instructor_profile import InstructorProfile
    id_card = db.query(InstructorProfile).filter(InstructorProfile.user_id == instructor.id).first()
    return templates.TemplateResponse("instructor/dashboard.html", {
        "request": request,
        "user": instructor,
        "active_page": "dashboard",
        "id_card": id_card,
    })


@router.get("/change-password")
def change_password_page(request: Request, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/change_password.html", {
        "request": request,
        "user": instructor,
        "active_page": "change_password",
        # Pass flag so template knows if this is a forced first-time change
        "is_forced": bool(instructor.must_change_password),
    })

@router.get("/satkit-training")
def satkit_training(request: Request, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/satkit_training.html", {
        "request": request, 
        "user": instructor,
        "active_page": "satkit"
    })

@router.get("/library")
def library(request: Request, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/library.html", {
        "request": request, 
        "user": instructor,
        "active_page": "library"
    })

@router.get("/profile")
def profile(request: Request, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/profile.html", {
        "request": request, 
        "user": instructor,
        "active_page": "profile"
    })

@router.get("/profile-card")
def profile_card(
    request: Request,
    instructor: User = Depends(get_current_instructor),
    db: Session = Depends(get_db),
):
    id_card = db.query(InstructorProfile).filter(
        InstructorProfile.user_id == instructor.id
    ).first()
    return templates.TemplateResponse("instructor/profile_card.html", {
        "request": request,
        "user": instructor,
        "active_page": "profile_card",
        "id_card": id_card,
    })

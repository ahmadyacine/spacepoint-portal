from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import settings
from app.routers.deps import get_db
from app.models.user import User, UserRole
from app.models.instructor_profile import InstructorProfile

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_current_instructor(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=302,
            headers={"Location": "/?login=true"}
        )
        
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise JWTError()
    except JWTError:
        raise HTTPException(
            status_code=302,
            headers={
                "Location": "/?login=true",
                "Set-Cookie": "access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
            }
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=302,
            headers={
                "Location": "/?login=true",
                "Set-Cookie": "access_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
            }
        )

    if user.role != UserRole.INSTRUCTOR and user.role != "INSTRUCTOR":
        if user.role == UserRole.ADMIN or user.role == "ADMIN":
            raise HTTPException(
                status_code=302,
                headers={"Location": "/admin/dashboard"}
            )
        else:
            raise HTTPException(
                status_code=302,
                headers={"Location": "/status"}
            )
            
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

@router.get("/training/player/{video_id}")
def training_player(request: Request, video_id: int, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/training_player.html", {
        "request": request, 
        "user": instructor,
        "video_id": video_id,
        "active_page": "satkit"
    })

@router.get("/library")
def library(request: Request, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/library.html", {
        "request": request, 
        "user": instructor,
        "active_page": "library"
    })

@router.get("/personal-documents")
def personal_documents(request: Request, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/personal_documents.html", {
        "request": request, 
        "user": instructor,
        "active_page": "personal_documents"
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

@router.get("/payments")
def payments_page(request: Request, instructor: User = Depends(get_current_instructor)):
    return templates.TemplateResponse("instructor/payments.html", {
        "request": request,
        "user": instructor,
        "active_page": "payments",
    })


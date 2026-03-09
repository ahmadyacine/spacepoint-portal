from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.routers.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.invitation import InvitationCode
from app.models.profile import ApplicantProfile
from app.models.review import ApplicationReview, ApplicationStatus
from app.schemas.core import UserCreate, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

router = APIRouter()

@router.get("/validate-invite/{code}")
def validate_invite(code: str, db: Session = Depends(get_db)):
    invite = db.query(InvitationCode).filter(InvitationCode.code == code).first()
    if not invite or not invite.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive invitation code")
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation code expired")
    if invite.used_count >= invite.max_uses:
        raise HTTPException(status_code=400, detail="Invitation code usage limit reached")
    return {"valid": True}

@router.post("/signup")
def signup(data: UserCreate, response: Response, db: Session = Depends(get_db)):
    # Validate invitation code
    invite = db.query(InvitationCode).filter(InvitationCode.code == data.invitation_code).first()
    if not invite or not invite.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive invitation code")
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation code expired")
    if invite.used_count >= invite.max_uses:
        raise HTTPException(status_code=400, detail="Invitation code usage limit reached")

    # Check email
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create User
    new_user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        role=UserRole.APPLICANT,
        invitation_code_used=data.invitation_code
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Increment invite count
    invite.used_count += 1
    
    # Create Profile
    profile = ApplicantProfile(
        user_id=new_user.id,
        university=data.university,
        highest_degree=data.highest_degree,
        highest_degree_other=data.highest_degree_other,
        city_of_residence=data.city_of_residence,
        deliver_cities_json=json.dumps(data.deliver_cities),
        background_areas_json=json.dumps(data.background_areas),
        background_other=data.background_other
    )
    db.add(profile)
    
    # Initialize application status
    app_review = ApplicationReview(
        user_id=new_user.id,
        status=ApplicationStatus.IN_PROGRESS
    )
    db.add(app_review)
    
    # Initialize 3 video assignments
    urls = [
        "https://youtu.be/6KcV1C1Ui5s?si=n_6wINrLhwe8JDuL",
        "https://youtu.be/qr1AvisQcV8?si=3vzFE1dRYqKiMKQS",
        "https://youtu.be/5voQfQOTem8?si=MZ5ztg6y9jiJASk6"
    ]
    from app.models.submission import VideoSubmission
    for i, url in enumerate(urls, 1):
        db.add(VideoSubmission(user_id=new_user.id, video_no=i, youtube_url=url))
    
    db.commit()

    # Create JWT
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    # Set Cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )

    return {"message": "Signup successful", "user_id": new_user.id}


@router.post("/login")
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return {"message": "Login successful", "role": user.role}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.post("/change-password")
def change_password(
    request_data: dict,
    user: User   = Depends(get_current_user),
    db: Session  = Depends(get_db),
):
    """
    Change the logged-in user's password.

    - If must_change_password is True (first login with temp password),
      current_password is NOT required — the system assigned it and the
      user just needs to set a new one.
    - Otherwise, current_password must be supplied and verified.
    """
    new_password     = request_data.get("new_password", "").strip()
    current_password = request_data.get("current_password", "").strip()

    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters.")

    if user.must_change_password:
        # First-time change after admin assigned temp password — no current_password needed
        pass
    else:
        # Regular change — must verify existing password
        if not current_password:
            raise HTTPException(status_code=400, detail="Current password is required.")
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")

    user.password_hash        = get_password_hash(new_password)
    user.must_change_password = 0   # clear the flag (stored as Integer)
    db.commit()

    return {"message": "Password changed successfully."}

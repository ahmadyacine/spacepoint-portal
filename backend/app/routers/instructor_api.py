"""
instructor_api.py
-----------------
API endpoints for instructor ID card generation and retrieval.
"""
import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.routers.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.instructor_profile import InstructorProfile
from app.models.review import ApplicationReview
from app.services.id_card_service import (
    generate_front_card, generate_back_card,
    save_instructor_cards,
)

router = APIRouter()

# ── Helpers ────────────────────────────────────────────────────────────────

def _require_instructor(user: User = Depends(get_current_user)):
    if user.role not in (UserRole.INSTRUCTOR, "INSTRUCTOR"):
        raise HTTPException(status_code=403, detail="Instructor access required")
    return user

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.normpath(os.path.join(_THIS_DIR, "..", ".."))
PHOTO_UPLOAD_DIR = os.path.join(_BACKEND_DIR, "app", "uploads", "instructor_photos")


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/id-card/generate")
def generate_id_card(
    linkedin_url: str    = Form(...),
    profile_image: UploadFile = File(...),
    instructor: User     = Depends(_require_instructor),
    db: Session          = Depends(get_db),
):
    """Generate (or regenerate) instructor ID card front + back PNGs."""

    # 1. Save profile photo to disk
    os.makedirs(PHOTO_UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(profile_image.filename or "photo.jpg")[1] or ".jpg"
    photo_path = os.path.join(PHOTO_UPLOAD_DIR, f"{instructor.id}{ext}")
    with open(photo_path, "wb") as f:
        shutil.copyfileobj(profile_image.file, f)

    # 2. Determine issue date from approval review
    review = db.query(ApplicationReview).filter(
        ApplicationReview.user_id == instructor.id
    ).first()
    issue_date = (
        review.reviewed_at if (review and review.reviewed_at)
        else datetime.utcnow()
    )

    # 3. Fetch existing profile (needed for upsert below)
    profile = db.query(InstructorProfile).filter(
        InstructorProfile.user_id == instructor.id
    ).first()

    # Derive instructor_id from user.id — matches the dashboard Instructor ID Pin
    ins_id = f"SP-{instructor.id:04d}-UAE"


    # 4. Generate card images
    front_img = generate_front_card(photo_path, linkedin_url, instructor.name)
    back_img  = generate_back_card(ins_id, issue_date)
    front_path, back_path = save_instructor_cards(instructor.id, front_img, back_img)

    # 5. Upsert InstructorProfile
    if not profile:
        profile = InstructorProfile(user_id=instructor.id)
        db.add(profile)

    profile.linkedin_url       = linkedin_url
    profile.profile_photo_path = photo_path
    profile.instructor_id      = ins_id
    profile.issue_date         = issue_date
    profile.front_card_path    = front_path
    profile.back_card_path     = back_path
    profile.updated_at         = datetime.utcnow()
    db.commit()
    db.refresh(profile)

    return {
        "success": True,
        "instructor_id": ins_id,
        "issue_date": issue_date.strftime("%d %B %Y"),
        "front_url": f"/api/instructor/id-card/front",
        "back_url":  f"/api/instructor/id-card/back",
    }


@router.get("/id-card")
def get_id_card_meta(
    instructor: User = Depends(_require_instructor),
    db: Session      = Depends(get_db),
):
    """Return metadata for the instructor's current ID card."""
    profile = db.query(InstructorProfile).filter(
        InstructorProfile.user_id == instructor.id
    ).first()
    if not profile:
        return {"generated": False}
    return {
        "generated":     bool(profile.front_card_path),
        "instructor_id": profile.instructor_id,
        "issue_date":    profile.issue_date.strftime("%d %B %Y") if profile.issue_date else None,
        "linkedin_url":  profile.linkedin_url,
        "front_url":     "/api/instructor/id-card/front" if profile.front_card_path else None,
        "back_url":      "/api/instructor/id-card/back"  if profile.back_card_path  else None,
    }


@router.get("/id-card/front")
def get_front_card(
    instructor: User = Depends(_require_instructor),
    db: Session      = Depends(get_db),
):
    """Stream the front card PNG."""
    profile = db.query(InstructorProfile).filter(
        InstructorProfile.user_id == instructor.id
    ).first()
    if not profile or not profile.front_card_path or not os.path.exists(profile.front_card_path):
        raise HTTPException(status_code=404, detail="Front card not generated yet")
    return FileResponse(profile.front_card_path, media_type="image/png")


@router.get("/id-card/back")
def get_back_card(
    instructor: User = Depends(_require_instructor),
    db: Session      = Depends(get_db),
):
    """Stream the back card PNG."""
    profile = db.query(InstructorProfile).filter(
        InstructorProfile.user_id == instructor.id
    ).first()
    if not profile or not profile.back_card_path or not os.path.exists(profile.back_card_path):
        raise HTTPException(status_code=404, detail="Back card not generated yet")
    return FileResponse(profile.back_card_path, media_type="image/png")

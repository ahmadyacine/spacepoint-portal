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
from app.models.library import LibraryResource
from app.models.training import TrainingModule, TrainingVideo, UserTrainingProgress
from app.models.instructor_document import InstructorDocument

router = APIRouter()

# ── Helpers ────────────────────────────────────────────────────────────────

def _require_instructor(user: User = Depends(get_current_user)):
    if user.role not in (UserRole.INSTRUCTOR, "INSTRUCTOR"):
        raise HTTPException(status_code=403, detail="Instructor access required")
    return user

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.normpath(os.path.join(_THIS_DIR, "..", ".."))
PHOTO_UPLOAD_DIR = os.path.join(_BACKEND_DIR, "app", "uploads", "instructor_photos")
DOCUMENTS_UPLOAD_DIR = os.path.join(_BACKEND_DIR, "app", "uploads", "instructor_documents")


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

@router.get("/download/{resource_id}")
def download_library_resource(
    resource_id: int,
    instructor: User = Depends(_require_instructor),
    db: Session      = Depends(get_db)
):
    """Download a library resource file."""
    resource = db.query(LibraryResource).filter(LibraryResource.id == resource_id).first()
    if not resource or not os.path.exists(resource.file_path):
        raise HTTPException(status_code=404, detail="Resource not found")
        
    return FileResponse(
        path=resource.file_path, 
        filename=os.path.basename(resource.file_path).split('_', 1)[-1], # remove timestamp prefix for download name
    )

@router.get("/view/{resource_id}")
def view_library_resource(
    resource_id: int,
    instructor: User = Depends(_require_instructor),
    db: Session      = Depends(get_db)
):
    """View a library resource file inline in the browser."""
    resource = db.query(LibraryResource).filter(LibraryResource.id == resource_id).first()
    if not resource or not os.path.exists(resource.file_path):
        raise HTTPException(status_code=404, detail="Resource not found")
        
    import mimetypes
    media_type, _ = mimetypes.guess_type(resource.file_path)
    if not media_type:
        media_type = "application/octet-stream"
        
    # Standard python mimetypes doesn't always know all formats
    return FileResponse(
        path=resource.file_path,
        media_type=media_type,
        content_disposition_type="inline"
    )

# --------------------------------------------------------------------------------
# PERSONAL DOCUMENTS (INSTRUCTOR LIBRARY)
# --------------------------------------------------------------------------------

@router.post("/library/personal-documents")
def upload_personal_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    instructor: User = Depends(_require_instructor),
    db: Session = Depends(get_db)
):
    os.makedirs(DOCUMENTS_UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{instructor.id}_{document_type.replace(' ', '_')}_{timestamp}{ext}"
    file_path = os.path.join(DOCUMENTS_UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    doc = InstructorDocument(
        user_id=instructor.id,
        document_type=document_type,
        file_path=file_path
    )
    db.add(doc)
    db.commit()
    return {"success": True, "message": "Document uploaded successfully"}

@router.get("/library/personal-documents")
def get_personal_documents(
    instructor: User = Depends(_require_instructor),
    db: Session = Depends(get_db)
):
    docs = db.query(InstructorDocument).filter(InstructorDocument.user_id == instructor.id).all()
    return [
        {
            "id": doc.id,
            "document_type": doc.document_type,
            "filename": os.path.basename(doc.file_path),
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None
        }
        for doc in docs
    ]

@router.delete("/library/personal-documents/{doc_id}")
def delete_personal_document(
    doc_id: int,
    instructor: User = Depends(_require_instructor),
    db: Session = Depends(get_db)
):
    doc = db.query(InstructorDocument).filter(
        InstructorDocument.id == doc_id, 
        InstructorDocument.user_id == instructor.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
        
    db.delete(doc)
    db.commit()
    return {"success": True}

@router.get("/library/personal-documents/{doc_id}/download")
def download_personal_document(
    doc_id: int,
    instructor: User = Depends(_require_instructor),
    db: Session = Depends(get_db)
):
    doc = db.query(InstructorDocument).filter(
        InstructorDocument.id == doc_id, 
        InstructorDocument.user_id == instructor.id
    ).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Document not found")
        
    return FileResponse(doc.file_path, filename=os.path.basename(doc.file_path))

# --------------------------------------------------------------------------------
# SATKIT TRAINING MODULES (INSTRUCTOR)
# --------------------------------------------------------------------------------

@router.get("/training/modules")
def get_instructor_training_modules(db: Session = Depends(get_db), current_user: User = Depends(_require_instructor)):
    # 1. Fetch all modules and their videos
    modules = db.query(TrainingModule).order_by(TrainingModule.sort_order.asc(), TrainingModule.id.asc()).all()
    
    # 2. Fetch the user's completed videos
    progress = db.query(UserTrainingProgress).filter(
        UserTrainingProgress.user_id == current_user.id,
        UserTrainingProgress.is_completed == True
    ).all()
    completed_video_ids = {p.video_id for p in progress}

    result = []
    for mod in modules:
        vids = sorted(mod.videos, key=lambda x: x.sort_order)
        mod_videos = []
        for v in vids:
            mod_videos.append({
                "id": v.id,
                "title": v.title,
                "description": v.description,
                "sort_order": v.sort_order,
                "is_completed": v.id in completed_video_ids
            })
            
        result.append({
            "id": mod.id,
            "title": mod.title,
            "description": mod.description,
            "sort_order": mod.sort_order,
            "videos": mod_videos,
            "completed_count": sum(1 for v in mod_videos if v["is_completed"]),
            "total_count": len(mod_videos)
        })
        
    return result

@router.get("/training/videos/{video_id}")
def get_instructor_training_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(_require_instructor)):
    video = db.query(TrainingVideo).filter(TrainingVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    completion = db.query(UserTrainingProgress).filter(
        UserTrainingProgress.user_id == current_user.id,
        UserTrainingProgress.video_id == video.id
    ).first()
    
    return {
        "id": video.id,
        "module_id": video.module_id,
        "title": video.title,
        "description": video.description,
        "notes": video.notes,
        "is_completed": bool(completion and completion.is_completed)
    }

@router.get("/training/stream/{video_id}")
def stream_training_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(_require_instructor)):
    video = db.query(TrainingVideo).filter(TrainingVideo.id == video_id).first()
    if not video or not os.path.exists(video.video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
        
    # Standard file response is okay for small mp4s, 
    # but a true streaming response might be better long-term.
    return FileResponse(video.video_path, media_type="video/mp4")

@router.post("/training/videos/{video_id}/complete")
def complete_training_video(video_id: int, db: Session = Depends(get_db), current_user: User = Depends(_require_instructor)):
    video = db.query(TrainingVideo).filter(TrainingVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    progress = db.query(UserTrainingProgress).filter(
        UserTrainingProgress.user_id == current_user.id,
        UserTrainingProgress.video_id == video_id
    ).first()
    
    if not progress:
        progress = UserTrainingProgress(
            user_id=current_user.id,
            video_id=video_id,
        )
        db.add(progress)
        
    progress.is_completed = True
    progress.completed_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "message": "Video marked as complete"}

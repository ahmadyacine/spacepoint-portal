from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from app.routers.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.submission import VideoSubmission, ResearchSubmission, SubmissionStatus
from app.models.review import ApplicationReview, ApplicationStatus
from app.schemas.core import VideoSummaryUpdate

router = APIRouter()

@router.get("/videos")
def get_videos(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subs = db.query(VideoSubmission).filter(VideoSubmission.user_id == user.id).order_by(VideoSubmission.video_no).all()
    return subs

@router.put("/videos/{video_no}")
def update_video_summary(video_no: int, data: VideoSummaryUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sub = db.query(VideoSubmission).filter(VideoSubmission.user_id == user.id, VideoSubmission.video_no == video_no).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Video assignment not found")
        
    if sub.status == SubmissionStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Already submitted")

    words = len(data.summary_text.split())
    if data.status == SubmissionStatus.SUBMITTED and words < 200:
        raise HTTPException(status_code=400, detail="Summary must be at least 200 words to submit")
        
    sub.summary_text = data.summary_text
    sub.word_count = words
    sub.status = data.status
    if data.status == SubmissionStatus.SUBMITTED:
        sub.submitted_at = datetime.utcnow()
        
    db.commit()
    return {"message": "Success"}

@router.get("/modules")
def get_modules(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.checklist import Module, ModuleSection, ChecklistItem, ModuleSubmission, UserChecklistProgress
    
    modules = db.query(Module).order_by(Module.sort_order).all()
    user_mod_subs = {
        sub.module_id: sub 
        for sub in db.query(ModuleSubmission).filter(ModuleSubmission.user_id == user.id).all()
    }
    user_progress = {
        prog.checklist_item_id: prog.is_completed
        for prog in db.query(UserChecklistProgress).filter(UserChecklistProgress.user_id == user.id).all()
    }
    
    result = []
    for mod in modules:
        mod_dict = {
            "id": mod.id,
            "title": mod.title,
            "sort_order": mod.sort_order,
            "total_items": 0,
            "completed_items": 0,
            "submission_status": user_mod_subs[mod.id].status if mod.id in user_mod_subs else None
        }
        
        items = db.query(ChecklistItem).filter(ChecklistItem.module_id == mod.id).all()
        mod_dict["total_items"] = len(items)
        mod_dict["completed_items"] = sum(1 for item in items if user_progress.get(item.id))
        
        result.append(mod_dict)
        
    return result

@router.get("/modules/{module_id}")
def get_module_detail(module_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.checklist import Module, ModuleSection, ChecklistItem, ModuleSubmission, UserChecklistProgress
    
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    mod_sub = db.query(ModuleSubmission).filter(ModuleSubmission.user_id == user.id, ModuleSubmission.module_id == module_id).first()
    
    user_progress = {
        prog.checklist_item_id: prog.is_completed
        for prog in db.query(UserChecklistProgress).filter(UserChecklistProgress.user_id == user.id).all()
    }
    
    sections_query = db.query(ModuleSection).filter(ModuleSection.module_id == module_id).order_by(ModuleSection.sort_order).all()
    
    items_no_section = db.query(ChecklistItem).filter(
        ChecklistItem.module_id == module_id, 
        ChecklistItem.section_id == None
    ).order_by(ChecklistItem.sort_order).all()
    
    result = {
        "id": module.id,
        "title": module.title,
        "submission": {
            "id": mod_sub.id,
            "file_path": mod_sub.file_path,
            "status": mod_sub.status,
            "submitted_at": mod_sub.submitted_at,
            "feedback": mod_sub.feedback
        } if mod_sub else None,
        "sections": [],
        "items_no_section": []
    }
    
    for item in items_no_section:
        result["items_no_section"].append({
            "id": item.id,
            "item_code": item.item_code,
            "title": item.title,
            "description": item.description,
            "is_required": item.is_required,
            "is_completed": user_progress.get(item.id, False)
        })
        
    for sec in sections_query:
        sec_dict = {
            "id": sec.id,
            "title": sec.title,
            "items": []
        }
        items = db.query(ChecklistItem).filter(ChecklistItem.section_id == sec.id).order_by(ChecklistItem.sort_order).all()
        for item in items:
            sec_dict["items"].append({
                "id": item.id,
                "item_code": item.item_code,
                "title": item.title,
                "description": item.description,
                "is_required": item.is_required,
                "is_completed": user_progress.get(item.id, False)
            })
        result["sections"].append(sec_dict)
        
    return result

from pydantic import BaseModel
class ToggleItemRequest(BaseModel):
    is_completed: bool

@router.put("/checklist/items/{item_id}/toggle")
def toggle_checklist_item(
    item_id: int,
    data: ToggleItemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.checklist import ChecklistItem, UserChecklistProgress
    
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
        
    progress = db.query(UserChecklistProgress).filter(
        UserChecklistProgress.user_id == user.id,
        UserChecklistProgress.checklist_item_id == item_id
    ).first()
    
    if progress:
        progress.is_completed = data.is_completed
    else:
        new_prog = UserChecklistProgress(
            user_id=user.id,
            checklist_item_id=item_id,
            is_completed=data.is_completed
        )
        db.add(new_prog)
        
    db.commit()
    return {"message": "Success"}

@router.post("/modules/{module_id}/submit")
def submit_module(
    module_id: int,
    file: UploadFile = File(...),
    notes_text: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.checklist import Module, ModuleSubmission
    
    subs = db.query(VideoSubmission).filter(VideoSubmission.user_id == user.id).all()
    if len(subs) != 3 or any(s.status != SubmissionStatus.SUBMITTED for s in subs):
        raise HTTPException(status_code=400, detail="Must submit all video summaries before unlocking modules.")

    review = db.query(ApplicationReview).filter(ApplicationReview.user_id == user.id).first()
    if review and review.status != ApplicationStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Application already submitted, cannot modify.")
        
    mod = db.query(Module).filter(Module.id == module_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found")
        
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "modules")
    os.makedirs(upload_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{user.id}_{module_id}_{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    existing_sub = db.query(ModuleSubmission).filter(
        ModuleSubmission.user_id == user.id, 
        ModuleSubmission.module_id == module_id
    ).first()
    
    if existing_sub:
        existing_sub.file_path = file_path
        existing_sub.original_filename = file.filename
        existing_sub.notes_text = notes_text
        existing_sub.status = "SUBMITTED"
        existing_sub.submitted_at = datetime.utcnow()
    else:
        new_sub = ModuleSubmission(
            user_id=user.id,
            module_id=module_id,
            file_path=file_path,
            original_filename=file.filename,
            notes_text=notes_text,
            status="SUBMITTED"
        )
        db.add(new_sub)
        
    db.commit()
    
    return {"message": "Module submitted successfully"}

@router.post("/application/submit")
def submit_final_application(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.checklist import Module, ModuleSubmission
    
    video_subs = db.query(VideoSubmission).filter(VideoSubmission.user_id == user.id).all()
    if len(video_subs) != 3 or any(s.status != SubmissionStatus.SUBMITTED for s in video_subs):
        raise HTTPException(status_code=400, detail="Must submit all video summaries first")
        
    total_modules = db.query(Module).count()
    user_mod_subs = db.query(ModuleSubmission).filter(ModuleSubmission.user_id == user.id).all()
    valid_subs = [s for s in user_mod_subs if s.status in ["SUBMITTED", "APPROVED"]]
    
    if len(valid_subs) != total_modules:
        raise HTTPException(status_code=400, detail=f"Missing module submissions. You need {total_modules} module submissions.")
        
    review = db.query(ApplicationReview).filter(ApplicationReview.user_id == user.id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review record not found")
        
    if review.status != ApplicationStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Application already submitted")
        
    review.status = ApplicationStatus.UNDER_REVIEW
    db.commit()
    
    return {"message": "Application submitted successfully"}

@router.post("/application/reopen")
def reopen_application(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = db.query(ApplicationReview).filter(ApplicationReview.user_id == user.id).first()
    if not review or review.status != ApplicationStatus.REJECTED:
        raise HTTPException(status_code=400, detail="Only rejected applications can be reopened.")
        
    review.status = ApplicationStatus.IN_PROGRESS
    db.commit()
    return {"message": "Application reopened successfully"}

@router.post("/presentation/submit")
def submit_presentation_link(
    video_link: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.submission import PresentationSubmission
    
    review = db.query(ApplicationReview).filter(ApplicationReview.user_id == user.id).first()
    if not review or review.status != ApplicationStatus.PHASE_1_APPROVED:
        raise HTTPException(status_code=400, detail="Not eligible to submit presentation at this stage.")
        
    existing_sub = db.query(PresentationSubmission).filter(PresentationSubmission.user_id == user.id).first()
    
    if existing_sub:
        existing_sub.video_link = video_link
        existing_sub.submitted_at = datetime.utcnow()
    else:
        new_sub = PresentationSubmission(
            user_id=user.id,
            video_link=video_link
        )
        db.add(new_sub)
        
    # Change status back to UNDER_REVIEW so admin knows Phase 2 was submitted
    review.status = ApplicationStatus.UNDER_REVIEW
    db.commit()
    
    return {"message": "Presentation link submitted successfully"}

@router.get("/status")
def get_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.checklist import ModuleSubmission
    from app.models.submission import PresentationSubmission
    
    review = db.query(ApplicationReview).filter(ApplicationReview.user_id == user.id).first()
    
    latest_sub = db.query(ModuleSubmission).filter(ModuleSubmission.user_id == user.id).order_by(ModuleSubmission.submitted_at.desc()).first()
    
    presentation = db.query(PresentationSubmission).filter(PresentationSubmission.user_id == user.id).first()
    
    return {
        "status": review.status if review else "NOT_STARTED",
        "feedback": review.feedback if review and review.status in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED] else None,
        "submitted_at": latest_sub.submitted_at if latest_sub else None,
        "presentation_link": presentation.video_link if presentation else None
    }

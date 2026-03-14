from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil

from app.routers.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.library import LibraryResource, LibraryModule
from app.models.training import TrainingModule, TrainingVideo

router = APIRouter()

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", "uploads", "library_resources")
os.makedirs(UPLOADS_DIR, exist_ok=True)

TRAINING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", "uploads", "training_videos")
os.makedirs(TRAINING_DIR, exist_ok=True)

@router.get("/library/modules")
def get_library_modules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Any authenticated user can view resources
    modules = db.query(LibraryModule).order_by(LibraryModule.name.asc()).all()
    result = []
    for mod in modules:
        result.append({
            "id": mod.id,
            "name": mod.name,
            "description": mod.description,
            "created_at": mod.created_at,
            "resources": [
                {
                    "id": res.id,
                    "title": res.title,
                    "description": res.description,
                    "format": res.format,
                    "created_at": res.created_at
                } for res in mod.resources
            ]
        })
    return result

@router.post("/library/modules")
def create_library_module(
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    facilitator: User = Depends(get_current_user)
):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing = db.query(LibraryModule).filter(LibraryModule.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Module name already exists")
        
    module = LibraryModule(name=name, description=description)
    db.add(module)
    db.commit()
    db.refresh(module)
    return module

@router.delete("/library/modules/{module_id}")
def delete_library_module(module_id: int, db: Session = Depends(get_db), facilitator: User = Depends(get_current_user)):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    module = db.query(LibraryModule).filter(LibraryModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    # delete all associated files from disk first
    for res in module.resources:
        if os.path.exists(res.file_path):
            try:
                os.remove(res.file_path)
            except:
                pass
                
    db.delete(module)
    db.commit()
    return {"message": "Module deleted successfully"}

@router.post("/library")
def upload_library_resource(
    title: str = Form(...),
    description: str = Form(None),
    module_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    facilitator: User = Depends(get_current_user)
):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to upload resources")

    # Determine format
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "unknown"
    fmt = "PDF" if ext == "pdf" else "PPTX" if ext in ["ppt", "pptx"] else ext.upper()

    # Save file
    file_path = os.path.join(UPLOADS_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resource = LibraryResource(
        title=title,
        description=description,
        module_id=module_id,
        format=fmt,
        file_path=file_path,
        uploader_id=facilitator.id
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource

@router.delete("/library/{resource_id}")
def delete_library_resource(resource_id: int, db: Session = Depends(get_db), facilitator: User = Depends(get_current_user)):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to delete resources")
        
    resource = db.query(LibraryResource).filter(LibraryResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    # delete file if exists
    if os.path.exists(resource.file_path):
        try:
            os.remove(resource.file_path)
        except:
            pass
            
    db.delete(resource)
    db.commit()
    return {"message": "Deleted successfully"}


# --------------------------------------------------------------------------------
# SATKIT TRAINING MODULES (FACILITATOR/ADMIN)
# --------------------------------------------------------------------------------

@router.get("/training/modules")
def get_training_modules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    modules = db.query(TrainingModule).order_by(TrainingModule.sort_order.asc(), TrainingModule.id.asc()).all()
    result = []
    for mod in modules:
        result.append({
            "id": mod.id,
            "title": mod.title,
            "description": mod.description,
            "sort_order": mod.sort_order,
            "created_at": mod.created_at,
            "videos": [
                {
                    "id": vid.id,
                    "title": vid.title,
                    "description": vid.description,
                    "notes": vid.notes,
                    "sort_order": vid.sort_order,
                    "created_at": vid.created_at
                } for vid in sorted(mod.videos, key=lambda v: v.sort_order)
            ]
        })
    return result

@router.post("/training/modules")
def create_training_module(
    title: str = Form(...),
    description: str = Form(None),
    sort_order: int = Form(1),
    db: Session = Depends(get_db),
    facilitator: User = Depends(get_current_user)
):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing = db.query(TrainingModule).filter(TrainingModule.title == title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Module title already exists")
        
    module = TrainingModule(title=title, description=description, sort_order=sort_order)
    db.add(module)
    db.commit()
    db.refresh(module)
    return module

@router.delete("/training/modules/{module_id}")
def delete_training_module(module_id: int, db: Session = Depends(get_db), facilitator: User = Depends(get_current_user)):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    module = db.query(TrainingModule).filter(TrainingModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    for vid in module.videos:
        if os.path.exists(vid.video_path):
            try:
                os.remove(vid.video_path)
            except:
                pass
                
    db.delete(module)
    db.commit()
    return {"message": "Training module deleted successfully"}

@router.post("/training/videos")
def upload_training_video(
    module_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    notes: str = Form(None),
    sort_order: int = Form(1),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    facilitator: User = Depends(get_current_user)
):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")

    module = db.query(TrainingModule).filter(TrainingModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    file_path = os.path.join(TRAINING_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video = TrainingVideo(
        module_id=module_id,
        title=title,
        description=description,
        notes=notes,
        video_path=file_path,
        sort_order=sort_order
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

@router.delete("/training/videos/{video_id}")
def delete_training_video(video_id: int, db: Session = Depends(get_db), facilitator: User = Depends(get_current_user)):
    if facilitator.role not in [UserRole.FACILITATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    video = db.query(TrainingVideo).filter(TrainingVideo.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if os.path.exists(video.video_path):
        try:
            os.remove(video.video_path)
        except:
            pass
            
    db.delete(video)
    db.commit()
    return {"message": "Video deleted successfully"}

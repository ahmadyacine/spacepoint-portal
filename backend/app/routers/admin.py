from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import io

from app.routers.deps import get_db, get_current_admin
from app.models.user import User, UserRole
from app.models.profile import ApplicantProfile
from app.models.submission import VideoSubmission
from app.models.review import ApplicationReview
from app.models.checklist import Module, ModuleSection, ChecklistItem, ModuleSubmission, UserChecklistProgress
from app.models.invitation import InvitationCode
from app.models.instructor_profile import InstructorProfile
from app.schemas.core import AdminReviewUpdate
from app.core.security import get_password_hash
from pydantic import BaseModel, EmailStr

class ChecklistDecisionUpdate(BaseModel):
    status: str # APPROVED or REJECTED
    feedback: str = None

router = APIRouter()

class InvitationCodeCreate(BaseModel):
    code: str
    max_uses: int = 20
    is_active: bool = True

class InvitationCodeUpdate(BaseModel):
    is_active: bool

class FacilitatorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

@router.get("/stats")
def get_admin_stats(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_started = db.query(User).filter(User.role == UserRole.APPLICANT).count()
    
    approved = db.query(ApplicationReview).filter(ApplicationReview.status == "APPROVED").count()
    rejected = db.query(ApplicationReview).filter(ApplicationReview.status == "REJECTED").count()
    
    draft = db.query(User).outerjoin(ApplicationReview, User.id == ApplicationReview.user_id).filter(
        User.role == UserRole.APPLICANT,
        ApplicationReview.id == None
    ).count()

    most_used = db.query(InvitationCode).order_by(InvitationCode.used_count.desc()).first()
    most_used_code = most_used.code if most_used else None

    return {
        "total_started": total_started,
        "approved": approved,
        "rejected": rejected,
        "draft_unsubmitted": draft,
        "most_used_invitation_code": most_used_code
    }

@router.get("/applicants")
def list_applicants(
    page: int = 1, 
    limit: int = 10, 
    admin: User = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    from app.models.submission import PresentationSubmission
    skip = (page - 1) * limit
    
    query = db.query(User, ApplicationReview).join(ApplicationReview, User.id == ApplicationReview.user_id)
    total = query.count()
    results = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    applicants = []
    for user, review in results:
        profile = db.query(ApplicantProfile).filter(ApplicantProfile.user_id == user.id).first()
        presentation = db.query(PresentationSubmission).filter(PresentationSubmission.user_id == user.id).first()
        city = profile.city_of_residence if profile else "Unknown"
        applicants.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "city": city,
            "status": review.status,
            "created_at": user.created_at,
            "invitation_code_used": user.invitation_code_used,
            "presentation_link": presentation.video_link if presentation else None
        })
        
    return {
        "data": applicants,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/applicants/{user_id}")
def get_applicant_detail(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    from app.models.submission import PresentationSubmission
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    profile = db.query(ApplicantProfile).filter(ApplicantProfile.user_id == user.id).first()
    videos = db.query(VideoSubmission).filter(VideoSubmission.user_id == user.id).all()
    review = db.query(ApplicationReview).filter(ApplicationReview.user_id == user.id).first()
    presentation = db.query(PresentationSubmission).filter(PresentationSubmission.user_id == user.id).first()
    
    return {
        "user": user,
        "profile": profile,
        "videos": videos,
        "review": review,
        "presentation_link": presentation.video_link if presentation else None
    }

@router.delete("/applicants/{user_id}")
def delete_applicant(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    from app.models.submission import PresentationSubmission
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Applicant not found")
        
    db.query(ApplicantProfile).filter(ApplicantProfile.user_id == user_id).delete()
    db.query(VideoSubmission).filter(VideoSubmission.user_id == user_id).delete()
    db.query(ApplicationReview).filter(ApplicationReview.user_id == user_id).delete()
    db.query(PresentationSubmission).filter(PresentationSubmission.user_id == user_id).delete()
    db.query(ModuleSubmission).filter(ModuleSubmission.user_id == user_id).delete()
    db.query(UserChecklistProgress).filter(UserChecklistProgress.user_id == user_id).delete()
    
    # Finally, delete user
    db.delete(user)
    db.commit()
    return {"message": "Applicant deleted successfully"}

@router.get("/applicants/{user_id}/checklist")
def get_applicant_checklist(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    modules = db.query(Module).order_by(Module.sort_order).all()
    
    user_mod_subs = {
        sub.module_id: sub 
        for sub in db.query(ModuleSubmission).filter(ModuleSubmission.user_id == user_id).all()
    }
    
    user_progress = {
        prog.checklist_item_id: prog.is_completed
        for prog in db.query(UserChecklistProgress).filter(UserChecklistProgress.user_id == user_id).all()
    }
    
    result = []
    for mod in modules:
        mod_sub = user_mod_subs.get(mod.id)
        mod_dict = {
            "id": mod.id,
            "title": mod.title,
            "submission": {
                "id": mod_sub.id,
                "status": mod_sub.status,
                "file_path": mod_sub.file_path,
                "notes_text": mod_sub.notes_text,
                "feedback": mod_sub.feedback,
                "submitted_at": mod_sub.submitted_at
            } if mod_sub else None,
            "sections": [],
            "items_no_section": []
        }
        
        items_no_section = db.query(ChecklistItem).filter(
            ChecklistItem.module_id == mod.id, 
            ChecklistItem.section_id == None
        ).order_by(ChecklistItem.sort_order).all()
        
        for item in items_no_section:
            mod_dict["items_no_section"].append({
                "item_code": item.item_code,
                "title": item.title,
                "is_completed": user_progress.get(item.id, False)
            })
            
        sections = db.query(ModuleSection).filter(ModuleSection.module_id == mod.id).order_by(ModuleSection.sort_order).all()
        for sec in sections:
            sec_dict = {
                "title": sec.title,
                "items": []
            }
            items = db.query(ChecklistItem).filter(ChecklistItem.section_id == sec.id).order_by(ChecklistItem.sort_order).all()
            for item in items:
                sec_dict["items"].append({
                    "item_code": item.item_code,
                    "title": item.title,
                    "is_completed": user_progress.get(item.id, False)
                })
            mod_dict["sections"].append(sec_dict)
            
        result.append(mod_dict)
        
    return result

@router.put("/modules/submissions/{submission_id}/decision")
def review_module_submission(submission_id: int, data: ChecklistDecisionUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    sub = db.query(ModuleSubmission).filter(ModuleSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    sub.status = data.status
    sub.feedback = data.feedback
    sub.reviewer_admin_id = admin.id
    sub.reviewed_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Module review updated"}

@router.put("/applicants/{user_id}/review")
def review_applicant(user_id: int, data: AdminReviewUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    review = db.query(ApplicationReview).filter(ApplicationReview.user_id == user_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Application not found")
        
    review.status = data.status
    review.feedback = data.feedback
    review.admin_id = admin.id
    review.reviewed_at = datetime.utcnow()
    
    email_sent = False
    user = db.query(User).filter(User.id == user_id).first()
    
    msg = "Review updated successfully"

    if data.status == "PHASE_1_APPROVED" and user:
        from app.services.email_service import send_phase1_approval_email
        email_sent = send_phase1_approval_email(to_email=user.email, name=user.name)
        if email_sent:
            msg = f"Phase 1 Approved. Email sent to {user.email}"
        else:
            msg = f"Phase 1 Approved, but email failed to send to {user.email}."

    elif data.status == "APPROVED" and user:
        from app.models.user import UserRole
        import secrets
        from app.core.security import get_password_hash
        from app.services.email_service import send_approval_credentials_email
        
        # Always regenerate password and send email on approval (handles re-approvals too)
        temp_password = secrets.token_urlsafe(12)
        user.password_hash = get_password_hash(temp_password)
        user.role = UserRole.INSTRUCTOR
        user.must_change_password = 1   # INTEGER column — use 1/0 not True/False
        user.temp_password_last_set_at = datetime.utcnow()
        
        profile = db.query(ApplicantProfile).filter(ApplicantProfile.user_id == user.id).first()
        living_area = profile.city_of_residence if profile else "Unknown"
        
        email_sent, contract_path = send_approval_credentials_email(
            to_email=user.email,
            name=user.name,
            temp_password=temp_password,
            living_area=living_area
        )
        
        # Save contract record to the database
        inst_profile = db.query(InstructorProfile).filter(InstructorProfile.user_id == user.id).first()
        if not inst_profile:
            inst_profile = InstructorProfile(user_id=user.id)
            db.add(inst_profile)
        
        inst_profile.contract_path = contract_path
        # We can also set an initial instructor ID if wanted, or leave it for later
        
        if email_sent:
            msg = f"Approved. Credentials email sent to {user.email}"
        else:
            msg = f"Approved, but credentials email failed to send to {user.email}."
            
    db.commit()
    return {"message": msg, "email_sent": email_sent}

@router.get("/modules/submissions/{submission_id}/download")
def download_single_submission(submission_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    sub = db.query(ModuleSubmission).filter(ModuleSubmission.id == submission_id).first()
    if not sub or not os.path.exists(sub.file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=sub.file_path,
        filename=sub.original_filename,
        media_type='application/pdf'
    )

@router.get("/applicants/{user_id}/export.pdf")
def export_applicant_pdf(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    from pypdf import PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    merger = PdfWriter()
    
    # Generate Cover Page
    cover_packet = io.BytesIO()
    can = canvas.Canvas(cover_packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 24)
    can.drawString(100, 700, "SpacePoint Instructor Application")
    can.setFont("Helvetica", 14)
    can.drawString(100, 660, f"Applicant: {user.name}")
    can.drawString(100, 640, f"Email: {user.email}")
    can.drawString(100, 620, f"Invitation Code: {user.invitation_code_used}")
    can.drawString(100, 600, f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    can.save()
    cover_packet.seek(0)
    merger.append(fileobj=cover_packet)
    
    modules = db.query(Module).order_by(Module.sort_order).all()
    user_mod_subs = {
        sub.module_id: sub 
        for sub in db.query(ModuleSubmission).filter(ModuleSubmission.user_id == user_id).all()
    }
    
    for mod in modules:
        # Generate Separator Page
        sep_packet = io.BytesIO()
        can = canvas.Canvas(sep_packet, pagesize=letter)
        can.setFont("Helvetica-Bold", 18)
        can.drawString(100, 700, f"Module: {mod.title}")
        
        can.setFont("Helvetica", 14)
        sub = user_mod_subs.get(mod.id)
        y = 660
        if sub and os.path.exists(sub.file_path):
            can.drawString(100, y, f"Status: {sub.status}")
            can.drawString(100, y - 20, f"Original File: {sub.original_filename}")
            if sub.notes_text:
                can.drawString(100, y - 40, f"Applicant Notes: {sub.notes_text}")
        else:
            can.setFillColorRGB(0.8, 0, 0)
            can.drawString(100, y, "STATUS: No module submission provided")
            
        can.save()
        sep_packet.seek(0)
        merger.append(fileobj=sep_packet)
        
        # Append applicant PDF if exists
        if sub and os.path.exists(sub.file_path):
            try:
                # Append exact file
                file_pdf = open(sub.file_path, "rb")
                merger.append(fileobj=file_pdf)
            except Exception as e:
                err_packet = io.BytesIO()
                can = canvas.Canvas(err_packet, pagesize=letter)
                can.drawString(100, 700, f"Error rendering PDF: {str(e)}")
                can.save()
                err_packet.seek(0)
                merger.append(fileobj=err_packet)
                
    output_pdf = io.BytesIO()
    merger.write(output_pdf)
    output_pdf.seek(0)
    
    return StreamingResponse(
        output_pdf, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=SpacePoint_Application_{user_id}.pdf"}
    )

@router.get("/invitations")
def list_invitations(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    invitations = db.query(InvitationCode).order_by(InvitationCode.created_at.desc()).all()
    return invitations

@router.post("/invitations")
def create_invitation(data: InvitationCodeCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    existing = db.query(InvitationCode).filter(InvitationCode.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Invitation code already exists")
        
    new_code = InvitationCode(
        code=data.code,
        max_uses=data.max_uses,
        is_active=data.is_active
    )
    db.add(new_code)
    db.commit()
    db.refresh(new_code)
    return new_code

@router.put("/invitations/{invitation_id}")
def update_invitation(invitation_id: int, data: InvitationCodeUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    invitation = db.query(InvitationCode).filter(InvitationCode.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation code not found")
        
    invitation.is_active = data.is_active
    db.commit()
    db.refresh(invitation)
    return invitation

@router.delete("/invitations/{invitation_id}")
def delete_invitation(invitation_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    invitation = db.query(InvitationCode).filter(InvitationCode.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation code not found")
        
    db.delete(invitation)
@router.get("/facilitators")
def list_facilitators(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    facilitators = db.query(User).filter(User.role == UserRole.FACILITATOR).order_by(User.created_at.desc()).all()
    return [{"id": f.id, "name": f.name, "email": f.email, "created_at": f.created_at} for f in facilitators]

@router.post("/facilitators")
def create_facilitator(data: FacilitatorCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
        
    hashed_password = get_password_hash(data.password)
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_password,
        role=UserRole.FACILITATOR,
        must_change_password=0
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email, "role": new_user.role}

from app.models.instructor_document import InstructorDocument
import mimetypes

@router.get("/instructors")
def list_instructors(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    instructors = db.query(User).filter(User.role == UserRole.INSTRUCTOR).order_by(User.created_at.desc()).all()
    res = []
    for ins in instructors:
        profile = db.query(ApplicantProfile).filter(ApplicantProfile.user_id == ins.id).first()
        city = profile.city_of_residence if profile else "Unknown"
        res.append({
            "id": ins.id,
            "name": ins.name,
            "email": ins.email,
            "phone": ins.phone,
            "city": city,
            "created_at": ins.created_at
        })
    return res

@router.get("/instructors/{user_id}")
def get_instructor_detail(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.INSTRUCTOR).first()
    if not user:
        raise HTTPException(status_code=404, detail="Instructor not found")
        
    profile = db.query(ApplicantProfile).filter(ApplicantProfile.user_id == user.id).first()
    documents = db.query(InstructorDocument).filter(InstructorDocument.user_id == user.id).all()
    inst_profile = db.query(InstructorProfile).filter(InstructorProfile.user_id == user.id).first()
    
    return {
        "user": user,
        "profile": profile,
        "documents": documents,
        "inst_profile": inst_profile
    }

@router.get("/instructors/documents/{doc_id}/view")
def view_instructor_document(doc_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    doc = db.query(InstructorDocument).filter(InstructorDocument.id == doc_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Document not found")
        
    mime_type, _ = mimetypes.guess_type(doc.file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
        
    filename = os.path.basename(doc.file_path)
    return FileResponse(
        path=doc.file_path,
        media_type=mime_type,
        filename=filename,
        content_disposition_type="inline"
    )

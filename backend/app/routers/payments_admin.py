"""
payments_admin.py
-----------------
Admin-side API for managing payment batches, letters, sessions, add-ons,
bulk Excel import, and portal settings (admin signature).
"""

import os
import shutil
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.routers.deps import get_db, get_current_admin
from app.models.user import User, UserRole
from app.models.payment import (
    PaymentBatch, PaymentLetter, PaymentLetterStatus,
    PaymentSession, PaymentAddon, InstructorBankDetails, PortalSetting,
    SessionRole
)
from app.services.payment_service import (
    generate_payment_letter_pdf, parse_excel_bulk_import, generate_excel_template
)
from app.services.email_service import (
    send_payment_letter_ready_email, send_payment_signed_notification_email
)

router = APIRouter()

_UPLOADS_SETTINGS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "uploads", "settings"
)
os.makedirs(_UPLOADS_SETTINGS, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Portal Settings (admin signature image + signatory name)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/settings")
def get_portal_settings(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    rows = db.query(PortalSetting).all()
    return {r.key: r.value for r in rows}


@router.post("/settings")
def upsert_portal_setting(
    key: str = Form(...),
    value: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    row = db.query(PortalSetting).filter(PortalSetting.key == key).first()
    if row:
        row.value = value
    else:
        row = PortalSetting(key=key, value=value)
        db.add(row)
    db.commit()
    return {"ok": True, "key": key, "value": value}


@router.post("/settings/admin-signature")
async def upload_admin_signature(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (PNG, JPEG, etc.)")

    ext = os.path.splitext(file.filename)[1] or ".png"
    dest = os.path.join(_UPLOADS_SETTINGS, f"admin_signature{ext}")
    with open(dest, "wb") as f:
        f.write(await file.read())

    # Save path to portal_settings
    row = db.query(PortalSetting).filter(PortalSetting.key == "admin_signature_path").first()
    if row:
        row.value = dest
    else:
        row = PortalSetting(key="admin_signature_path", value=dest)
        db.add(row)
    db.commit()
    return {"ok": True, "path": dest}


# ══════════════════════════════════════════════════════════════════════════════
# Payment Batches
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/payments/batches")
def list_batches(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    batches = db.query(PaymentBatch).order_by(PaymentBatch.created_at.desc()).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "created_at": b.created_at.isoformat() if b.created_at else None,
            "letter_count": len(b.letters),
        }
        for b in batches
    ]


@router.post("/payments/batches")
def create_batch(
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    batch = PaymentBatch(name=name, description=description, created_by_admin_id=admin.id)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return {"ok": True, "id": batch.id, "name": batch.name}


@router.put("/payments/batches/{batch_id}")
def update_batch(
    batch_id: int,
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    batch = db.query(PaymentBatch).filter(PaymentBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")
    batch.name = name
    batch.description = description
    db.commit()
    return {"ok": True}


@router.delete("/payments/batches/{batch_id}")
def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    batch = db.query(PaymentBatch).filter(PaymentBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(404, "Batch not found")
    db.delete(batch)
    db.commit()
    return {"ok": True}


# ══════════════════════════════════════════════════════════════════════════════
# Payment Letters
# ══════════════════════════════════════════════════════════════════════════════

def _letter_to_dict(letter: PaymentLetter, db: Session) -> dict:
    instructor = db.query(User).filter(User.id == letter.instructor_user_id).first()
    sessions_total = sum(s.compensation_aed for s in letter.sessions)
    addons_total = sum(a.amount_aed for a in letter.addons)
    return {
        "id": letter.id,
        "batch_id": letter.batch_id,
        "instructor_user_id": letter.instructor_user_id,
        "instructor_name": instructor.name if instructor else "Unknown",
        "instructor_email": instructor.email if instructor else "",
        "letter_date": letter.letter_date,
        "reference": letter.reference,
        "status": letter.status.value if hasattr(letter.status, "value") else (letter.status or "DRAFT"),
        "is_published": letter.is_published,
        "signed_at": letter.signed_at.isoformat() if letter.signed_at else None,
        "admin_notes": letter.admin_notes,
        "has_pdf": bool(letter.pdf_path and os.path.exists(letter.pdf_path)),
        "has_signed_pdf": bool(letter.signed_pdf_path and os.path.exists(letter.signed_pdf_path)),
        "created_at": letter.created_at.isoformat() if letter.created_at else None,
        "sessions": [
            {
                "id": s.id,
                "session_date": s.session_date,
                "workshop_description": s.workshop_description,
                "role": s.role.value if hasattr(s.role, "value") else s.role,
                "location": s.location,
                "duration_hours": s.duration_hours,
                "compensation_aed": s.compensation_aed,
                "sort_order": s.sort_order,
            }
            for s in letter.sessions
        ],
        "addons": [
            {
                "id": a.id,
                "description": a.description,
                "amount_aed": a.amount_aed,
                "notes": a.notes,
                "sort_order": a.sort_order,
            }
            for a in letter.addons
        ],
        "sessions_total": sessions_total,
        "addons_total": addons_total,
        "grand_total": sessions_total + addons_total,
    }


@router.get("/payments/letters")
def list_all_letters(
    batch_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    q = db.query(PaymentLetter)
    if batch_id:
        q = q.filter(PaymentLetter.batch_id == batch_id)
    if status:
        q = q.filter(PaymentLetter.status == status)
    letters = q.order_by(PaymentLetter.created_at.desc()).all()
    return [_letter_to_dict(l, db) for l in letters]


@router.get("/payments/letters/{letter_id}")
def get_letter(
    letter_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    return _letter_to_dict(letter, db)


@router.post("/payments/letters")
def create_letter(
    instructor_user_id: int = Form(...),
    batch_id: Optional[int] = Form(None),
    letter_date: str = Form(""),
    reference: str = Form("Facilitator Agreement"),
    admin_notes: str = Form(""),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    # Verify instructor exists
    instructor = db.query(User).filter(
        User.id == instructor_user_id,
        User.role == UserRole.INSTRUCTOR
    ).first()
    if not instructor:
        raise HTTPException(404, "Instructor not found")

    letter = PaymentLetter(
        batch_id=batch_id or None,
        instructor_user_id=instructor_user_id,
        letter_date=letter_date or datetime.now().strftime("%d/%m/%Y"),
        reference=reference,
        admin_notes=admin_notes,
        status=PaymentLetterStatus.DRAFT,
    )
    db.add(letter)
    db.commit()
    db.refresh(letter)
    return {"ok": True, "id": letter.id}


@router.put("/payments/letters/{letter_id}")
def update_letter(
    letter_id: int,
    batch_id: Optional[int] = Form(None),
    letter_date: str = Form(""),
    reference: str = Form("Facilitator Agreement"),
    admin_notes: str = Form(""),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    letter.batch_id = batch_id or None
    letter.letter_date = letter_date
    letter.reference = reference
    letter.admin_notes = admin_notes
    db.commit()
    return {"ok": True}


@router.delete("/payments/letters/{letter_id}")
def delete_letter(
    letter_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    db.delete(letter)
    db.commit()
    return {"ok": True}


# ── Sessions CRUD ─────────────────────────────────────────────────────────

@router.post("/payments/letters/{letter_id}/sessions")
def add_session(
    letter_id: int,
    session_date: str = Form(...),
    workshop_description: str = Form(...),
    role: str = Form(...),
    location: str = Form(...),
    duration_hours: float = Form(...),
    compensation_aed: float = Form(...),
    sort_order: int = Form(1),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")

    try:
        role_enum = SessionRole(role)
    except ValueError:
        raise HTTPException(400, f"Invalid role: {role}. Must be one of: {[r.value for r in SessionRole]}")

    session = PaymentSession(
        payment_letter_id=letter_id,
        session_date=session_date,
        workshop_description=workshop_description,
        role=role_enum,
        location=location,
        duration_hours=duration_hours,
        compensation_aed=compensation_aed,
        sort_order=sort_order,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"ok": True, "id": session.id}


@router.put("/payments/sessions/{session_id}")
def update_session(
    session_id: int,
    session_date: str = Form(...),
    workshop_description: str = Form(...),
    role: str = Form(...),
    location: str = Form(...),
    duration_hours: float = Form(...),
    compensation_aed: float = Form(...),
    sort_order: int = Form(1),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    session = db.query(PaymentSession).filter(PaymentSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    try:
        role_enum = SessionRole(role)
    except ValueError:
        raise HTTPException(400, f"Invalid role: {role}")
    session.session_date = session_date
    session.workshop_description = workshop_description
    session.role = role_enum
    session.location = location
    session.duration_hours = duration_hours
    session.compensation_aed = compensation_aed
    session.sort_order = sort_order
    db.commit()
    return {"ok": True}


@router.delete("/payments/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    session = db.query(PaymentSession).filter(PaymentSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    db.delete(session)
    db.commit()
    return {"ok": True}


# ── Add-ons CRUD ──────────────────────────────────────────────────────────

@router.post("/payments/letters/{letter_id}/addons")
def add_addon(
    letter_id: int,
    description: str = Form(...),
    amount_aed: float = Form(...),
    notes: str = Form(""),
    sort_order: int = Form(1),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    addon = PaymentAddon(
        payment_letter_id=letter_id,
        description=description,
        amount_aed=amount_aed,
        notes=notes,
        sort_order=sort_order,
    )
    db.add(addon)
    db.commit()
    db.refresh(addon)
    return {"ok": True, "id": addon.id}


@router.put("/payments/addons/{addon_id}")
def update_addon(
    addon_id: int,
    description: str = Form(...),
    amount_aed: float = Form(...),
    notes: str = Form(""),
    sort_order: int = Form(1),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    addon = db.query(PaymentAddon).filter(PaymentAddon.id == addon_id).first()
    if not addon:
        raise HTTPException(404, "Add-on not found")
    addon.description = description
    addon.amount_aed = amount_aed
    addon.notes = notes
    addon.sort_order = sort_order
    db.commit()
    return {"ok": True}


@router.delete("/payments/addons/{addon_id}")
def delete_addon(
    addon_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    addon = db.query(PaymentAddon).filter(PaymentAddon.id == addon_id).first()
    if not addon:
        raise HTTPException(404, "Add-on not found")
    db.delete(addon)
    db.commit()
    return {"ok": True}


# ── PDF Generation + Publishing ────────────────────────────────────────────

@router.post("/payments/letters/{letter_id}/generate-pdf")
def generate_letter_pdf(
    letter_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    if not letter.sessions:
        raise HTTPException(400, "Cannot generate PDF: letter has no sessions.")

    pdf_path = generate_payment_letter_pdf(letter_id, db)
    if not pdf_path:
        raise HTTPException(500, "PDF generation failed")

    letter.status = PaymentLetterStatus.DRAFT
    db.commit()
    return {"ok": True, "message": "PDF generated successfully."}


@router.post("/payments/letters/{letter_id}/publish")
def publish_letter(
    letter_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    if not letter.pdf_path:
        # Auto-generate if not done yet
        pdf_path = generate_payment_letter_pdf(letter_id, db)
        if not pdf_path:
            raise HTTPException(500, "PDF generation failed. Cannot publish.")

    letter.is_published = True
    letter.status = PaymentLetterStatus.PUBLISHED
    db.commit()

    # Send email notification to instructor
    instructor = db.query(User).filter(User.id == letter.instructor_user_id).first()
    if instructor:
        try:
            from app.core.config import settings
            send_payment_letter_ready_email(
                to_email=instructor.email,
                instructor_name=instructor.name,
                portal_url=settings.BASE_URL.rstrip("/") + "/instructor/payments"
            )
        except Exception as e:
            print(f"[payments_admin] Email notification failed: {e}")

    return {"ok": True, "message": "Letter published and instructor notified."}


@router.post("/payments/letters/{letter_id}/mark-paid")
def mark_letter_paid(
    letter_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    letter.status = PaymentLetterStatus.PAID
    db.commit()
    return {"ok": True}


@router.get("/payments/letters/{letter_id}/download")
def download_letter_pdf(
    letter_id: int,
    signed: bool = False,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    letter = db.query(PaymentLetter).filter(PaymentLetter.id == letter_id).first()
    if not letter:
        raise HTTPException(404, "Letter not found")

    path = letter.signed_pdf_path if signed else letter.pdf_path
    if not path or not os.path.exists(path):
        raise HTTPException(404, "PDF not found. Generate the PDF first.")

    instructor = db.query(User).filter(User.id == letter.instructor_user_id).first()
    safe_name = instructor.name.replace(" ", "_") if instructor else "Instructor"
    filename = f"PaymentLetter_{safe_name}_{'Signed_' if signed else ''}{letter_id}.pdf"

    return FileResponse(path, media_type="application/pdf", filename=filename)


# ══════════════════════════════════════════════════════════════════════════════
# Bulk Excel Import
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/payments/bulk-import/preview")
async def bulk_import_preview(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Parse the Excel file and return a preview without saving to DB."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Please upload an Excel file (.xlsx)")

    content = await file.read()
    parsed = parse_excel_bulk_import(content)

    # Enrich with instructor lookup
    preview_rows = []
    unresolved_emails = []
    for email, data in parsed["instructors"].items():
        user = db.query(User).filter(User.email == email, User.role == UserRole.INSTRUCTOR).first()
        preview_rows.append({
            "email": email,
            "instructor_name": user.name if user else None,
            "instructor_found": bool(user),
            "session_count": len(data["sessions"]),
            "addon_count": len(data["addons"]),
            "sessions": data["sessions"],
            "addons": data["addons"],
            "base_total": sum(s["compensation_aed"] for s in data["sessions"]),
            "addons_total": sum(a["amount_aed"] for a in data["addons"]),
        })
        if not user:
            unresolved_emails.append(email)

    if unresolved_emails:
        parsed["errors"].append(
            f"Instructor emails not found in portal: {', '.join(unresolved_emails)}"
        )

    return {
        "preview": preview_rows,
        "errors": parsed["errors"],
        "instructor_count": len(preview_rows),
    }


@router.post("/payments/bulk-import/confirm")
async def bulk_import_confirm(
    file: UploadFile = File(...),
    batch_id: Optional[int] = Form(None),
    letter_date: str = Form(""),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Parse the Excel file and save all valid rows to DB."""
    content = await file.read()
    parsed = parse_excel_bulk_import(content)

    created_letters = []
    skipped = []

    for email, data in parsed["instructors"].items():
        user = db.query(User).filter(User.email == email, User.role == UserRole.INSTRUCTOR).first()
        if not user:
            skipped.append(email)
            continue

        if not data["sessions"]:
            skipped.append(f"{email} (no sessions)")
            continue

        letter = PaymentLetter(
            batch_id=batch_id or None,
            instructor_user_id=user.id,
            letter_date=letter_date or datetime.now().strftime("%d/%m/%Y"),
            reference="Facilitator Agreement",
            status=PaymentLetterStatus.DRAFT,
        )
        db.add(letter)
        db.flush()  # get the ID

        for idx, s in enumerate(data["sessions"]):
            try:
                role_enum = SessionRole(s["role"])
            except ValueError:
                role_enum = SessionRole.FACILITATOR
            session = PaymentSession(
                payment_letter_id=letter.id,
                session_date=s["session_date"],
                workshop_description=s["workshop_description"],
                role=role_enum,
                location=s["location"],
                duration_hours=s["duration_hours"],
                compensation_aed=s["compensation_aed"],
                sort_order=idx + 1,
            )
            db.add(session)

        for idx, a in enumerate(data["addons"]):
            addon = PaymentAddon(
                payment_letter_id=letter.id,
                description=a["description"],
                amount_aed=a["amount_aed"],
                notes=a.get("notes", ""),
                sort_order=idx + 1,
            )
            db.add(addon)

        created_letters.append({"email": email, "name": user.name, "letter_id": letter.id})

    db.commit()

    return {
        "ok": True,
        "created": len(created_letters),
        "skipped": len(skipped),
        "letters": created_letters,
        "errors": parsed["errors"],
    }


@router.get("/payments/bulk-import/template")
def download_excel_template(admin=Depends(get_current_admin)):
    """Download the blank Excel template for bulk import."""
    content = generate_excel_template()
    if not content:
        raise HTTPException(500, "Failed to generate template")

    from fastapi.responses import Response
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=SpacePoint_Payment_Import_Template.xlsx"}
    )


# ══════════════════════════════════════════════════════════════════════════════
# Instructors list (for dropdown)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/payments/instructors")
def list_instructors(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    instructors = db.query(User).filter(User.role == UserRole.INSTRUCTOR).order_by(User.name).all()
    return [{"id": u.id, "name": u.name, "email": u.email} for u in instructors]


# ══════════════════════════════════════════════════════════════════════════════
# Certificates Management
# ══════════════════════════════════════════════════════════════════════════════

from app.models.payment import Certificate
from app.services.payment_service import generate_certificate_pdf, _CERTIFICATE_UPLOADS_DIR
from app.services.email_service import send_certificates_email

@router.get("/payments/certificates")
def list_certificates(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    certs = db.query(Certificate).order_by(Certificate.created_at.desc()).all()
    res = []
    for c in certs:
        # Get user details for email
        instructor = db.query(User).filter(User.id == c.user_id).first()
        res.append({
            "id": c.id,
            "user_id": c.user_id,
            "payment_session_id": c.payment_session_id,
            "instructor_name": c.instructor_name,
            "instructor_email": instructor.email if instructor else "",
            "workshop_name": c.workshop_name,
            "workshop_date": c.workshop_date,
            "location": c.location,
            "pdf_path": c.pdf_path,
            "has_pdf": bool(c.pdf_path and os.path.exists(c.pdf_path)),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return res


@router.post("/payments/certificates")
def create_certificate(
    instructor_user_id: int = Form(...),
    workshop_name: str = Form(...),
    workshop_date: str = Form(...),
    location: str = Form(...),
    send_email: bool = Form(False),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == instructor_user_id, User.role == UserRole.INSTRUCTOR).first()
    if not user:
        raise HTTPException(404, "Instructor not found")

    cert = Certificate(
        user_id=instructor_user_id,
        payment_session_id=None,
        instructor_name=user.name,
        workshop_name=workshop_name,
        workshop_date=workshop_date,
        location=location,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    # Generate unique filename
    safe_inst_name = "".join(c for c in user.name if c.isalnum() or c in " _-").strip().replace(" ", "_")
    safe_ws_name = "".join(c for c in workshop_name if c.isalnum() or c in " _-").strip().replace(" ", "_")[:30]
    filename = f"Certificate_{safe_inst_name}_{cert.id}_{safe_ws_name}.pdf"
    
    cert_pdf_path = os.path.join(_CERTIFICATE_UPLOADS_DIR, filename)

    success = generate_certificate_pdf(
        pdf_path=cert_pdf_path,
        instructor_name=user.name,
        workshop_name=workshop_name,
        workshop_date=workshop_date,
        location=location
    )

    if not success:
        db.delete(cert)
        db.commit()
        raise HTTPException(500, "Failed to generate certificate PDF")

    cert.pdf_path = cert_pdf_path
    db.commit()

    if send_email:
        email_target = user.email
        if email_target in ["admin@spacepoint.com", "admin@spacepoint.ae"]:
            email_target = "ahmad2012yacine@gmail.com"
        send_certificates_email(to_email=email_target, name=user.name, pdf_paths=[cert_pdf_path])

    return {"ok": True, "id": cert.id}


@router.post("/payments/certificates/{cert_id}/email")
def email_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")
    
    user = db.query(User).filter(User.id == cert.user_id).first()
    if not user:
        raise HTTPException(404, "Instructor user not found")

    if not cert.pdf_path or not os.path.exists(cert.pdf_path):
        safe_inst_name = "".join(c for c in cert.instructor_name if c.isalnum() or c in " _-").strip().replace(" ", "_")
        safe_ws_name = "".join(c for c in cert.workshop_name if c.isalnum() or c in " _-").strip().replace(" ", "_")[:30]
        filename = f"Certificate_{safe_inst_name}_{cert.id}_{safe_ws_name}.pdf"
        cert.pdf_path = os.path.join(_CERTIFICATE_UPLOADS_DIR, filename)
        db.commit()

        success = generate_certificate_pdf(
            pdf_path=cert.pdf_path,
            instructor_name=cert.instructor_name,
            workshop_name=cert.workshop_name,
            workshop_date=cert.workshop_date,
            location=cert.location
        )
        if not success:
            raise HTTPException(500, "PDF missing and regeneration failed")

    email_target = user.email
    if email_target in ["admin@spacepoint.com", "admin@spacepoint.ae"]:
        email_target = "ahmad2012yacine@gmail.com"
    
    sent = send_certificates_email(to_email=email_target, name=cert.instructor_name, pdf_paths=[cert.pdf_path])
    if not sent:
        raise HTTPException(500, "Failed to send email")

    return {"ok": True, "message": "Email sent successfully"}


@router.delete("/payments/certificates/{cert_id}")
def delete_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    # Delete PDF file if exists
    if cert.pdf_path and os.path.exists(cert.pdf_path):
        try:
            os.remove(cert.pdf_path)
        except Exception as e:
            print(f"[payments_admin] Failed to delete certificate PDF file: {e}")

    db.delete(cert)
    db.commit()
    return {"ok": True}


@router.get("/payments/certificates/{cert_id}/download")
def download_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(404, "Certificate not found")

    if not cert.pdf_path or not os.path.exists(cert.pdf_path):
        safe_inst_name = "".join(c for c in cert.instructor_name if c.isalnum() or c in " _-").strip().replace(" ", "_")
        safe_ws_name = "".join(c for c in cert.workshop_name if c.isalnum() or c in " _-").strip().replace(" ", "_")[:30]
        filename = f"Certificate_{safe_inst_name}_{cert.id}_{safe_ws_name}.pdf"
        cert.pdf_path = os.path.join(_CERTIFICATE_UPLOADS_DIR, filename)
        db.commit()

        success = generate_certificate_pdf(
            pdf_path=cert.pdf_path,
            instructor_name=cert.instructor_name,
            workshop_name=cert.workshop_name,
            workshop_date=cert.workshop_date,
            location=cert.location
        )
        if not success:
            raise HTTPException(500, "PDF missing and regeneration failed")

    safe_inst_name = cert.instructor_name.replace(" ", "_")
    safe_ws_name = cert.workshop_name.replace(" ", "_")[:30]
    filename = f"Certificate_{safe_inst_name}_{cert.id}_{safe_ws_name}.pdf"

    return FileResponse(cert.pdf_path, media_type="application/pdf", filename=filename)


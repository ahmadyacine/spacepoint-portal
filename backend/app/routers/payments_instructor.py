"""
payments_instructor.py
-----------------------
Instructor-side API for viewing payment letters, signing, downloading PDFs,
and managing bank details.
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.routers.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.payment import (
    PaymentLetter, PaymentLetterStatus,
    PaymentSession, PaymentAddon, InstructorBankDetails
)
from app.services.payment_service import embed_instructor_signature
from app.services.email_service import send_payment_signed_notification_email

router = APIRouter()


def _require_instructor(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.INSTRUCTOR:
        raise HTTPException(403, "Not an instructor")
    return current_user


# ══════════════════════════════════════════════════════════════════════════════
# Bank Details
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/payments/bank-details")
def get_bank_details(
    db: Session = Depends(get_db),
    user: User = Depends(_require_instructor)
):
    bank = db.query(InstructorBankDetails).filter(
        InstructorBankDetails.user_id == user.id
    ).first()
    if not bank:
        return {
            "account_holder_name": "",
            "bank_name": "",
            "iban": "",
            "swift_bic": "",
        }
    return {
        "account_holder_name": bank.account_holder_name or "",
        "bank_name": bank.bank_name or "",
        "iban": bank.iban or "",
        "swift_bic": bank.swift_bic or "",
    }


@router.put("/payments/bank-details")
def save_bank_details(
    account_holder_name: str = Form(""),
    bank_name: str = Form(""),
    iban: str = Form(""),
    swift_bic: str = Form(""),
    db: Session = Depends(get_db),
    user: User = Depends(_require_instructor)
):
    bank = db.query(InstructorBankDetails).filter(
        InstructorBankDetails.user_id == user.id
    ).first()
    if bank:
        bank.account_holder_name = account_holder_name
        bank.bank_name = bank_name
        bank.iban = iban
        bank.swift_bic = swift_bic
    else:
        bank = InstructorBankDetails(
            user_id=user.id,
            account_holder_name=account_holder_name,
            bank_name=bank_name,
            iban=iban,
            swift_bic=swift_bic,
        )
        db.add(bank)
    db.commit()
    return {"ok": True, "message": "Bank details saved."}


# ══════════════════════════════════════════════════════════════════════════════
# Payment Letters — listing + detail
# ══════════════════════════════════════════════════════════════════════════════

def _letter_to_instructor_dict(letter: PaymentLetter) -> dict:
    sessions_total = sum(s.compensation_aed for s in letter.sessions)
    addons_total = sum(a.amount_aed for a in letter.addons)
    total_hours = sum(s.duration_hours for s in letter.sessions)
    return {
        "id": letter.id,
        "letter_date": letter.letter_date,
        "reference": letter.reference,
        "status": letter.status.value if hasattr(letter.status, "value") else (letter.status or "PUBLISHED"),
        "signed_at": letter.signed_at.isoformat() if letter.signed_at else None,
        "has_signed_pdf": bool(letter.signed_pdf_path and os.path.exists(letter.signed_pdf_path)),
        "sessions_total": sessions_total,
        "addons_total": addons_total,
        "grand_total": sessions_total + addons_total,
        "total_hours": total_hours,
        "session_count": len(letter.sessions),
        "sessions": [
            {
                "id": s.id,
                "session_date": s.session_date,
                "workshop_description": s.workshop_description,
                "role": s.role.value if hasattr(s.role, "value") else s.role,
                "location": s.location,
                "duration_hours": s.duration_hours,
                "compensation_aed": s.compensation_aed,
            }
            for s in letter.sessions
        ],
        "addons": [
            {
                "id": a.id,
                "description": a.description,
                "amount_aed": a.amount_aed,
                "notes": a.notes,
            }
            for a in letter.addons
        ],
    }


@router.get("/payments/letters")
def list_my_letters(
    db: Session = Depends(get_db),
    user: User = Depends(_require_instructor)
):
    letters = db.query(PaymentLetter).filter(
        PaymentLetter.instructor_user_id == user.id,
        PaymentLetter.is_published == True
    ).order_by(PaymentLetter.created_at.desc()).all()
    return [_letter_to_instructor_dict(l) for l in letters]


@router.get("/payments/letters/{letter_id}")
def get_my_letter(
    letter_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(_require_instructor)
):
    letter = db.query(PaymentLetter).filter(
        PaymentLetter.id == letter_id,
        PaymentLetter.instructor_user_id == user.id,
        PaymentLetter.is_published == True
    ).first()
    if not letter:
        raise HTTPException(404, "Letter not found")

    # Include bank details for display
    bank = db.query(InstructorBankDetails).filter(
        InstructorBankDetails.user_id == user.id
    ).first()
    data = _letter_to_instructor_dict(letter)
    data["bank"] = {
        "account_holder_name": bank.account_holder_name if bank else "",
        "bank_name": bank.bank_name if bank else "",
        "iban": bank.iban if bank else "",
        "swift_bic": bank.swift_bic if bank else "",
    }
    data["instructor_name"] = user.name
    return data


# ══════════════════════════════════════════════════════════════════════════════
# Digital Signature
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/payments/letters/{letter_id}/sign")
async def sign_letter(
    letter_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(_require_instructor)
):
    """
    Receives a JSON body: { "signature": "data:image/png;base64,..." }
    Embeds the signature into the PDF and marks the letter as SIGNED.
    """
    body = await request.json()
    signature_b64 = body.get("signature", "")

    if not signature_b64 or not signature_b64.startswith("data:image"):
        raise HTTPException(400, "Invalid signature data")

    letter = db.query(PaymentLetter).filter(
        PaymentLetter.id == letter_id,
        PaymentLetter.instructor_user_id == user.id,
        PaymentLetter.is_published == True
    ).first()
    if not letter:
        raise HTTPException(404, "Letter not found")
    status_str = letter.status.value if hasattr(letter.status, "value") else letter.status
    if status_str == "SIGNED" or status_str == PaymentLetterStatus.SIGNED:
        raise HTTPException(400, "Letter already signed")

    signed_pdf = embed_instructor_signature(letter_id, signature_b64, db)
    if not signed_pdf:
        raise HTTPException(500, "Failed to generate signed PDF")

    # Generate certificates for each session and email them
    try:
        from app.models.payment import Certificate
        from app.services.payment_service import generate_certificate_pdf, _CERTIFICATE_UPLOADS_DIR
        from app.services.email_service import send_certificates_email
        
        pdf_paths = []
        for session in letter.sessions:
            # Check if a certificate already exists for this session to avoid duplicates
            cert = db.query(Certificate).filter(Certificate.payment_session_id == session.id).first()
            if not cert:
                cert = Certificate(
                    user_id=user.id,
                    payment_session_id=session.id,
                    instructor_name=user.name,
                    workshop_name=session.workshop_description,
                    workshop_date=session.session_date,
                    location=session.location,
                )
                db.add(cert)
                db.commit()
                db.refresh(cert)

            # Generate unique filename
            safe_inst_name = "".join(c for c in user.name if c.isalnum() or c in " _-").strip().replace(" ", "_")
            safe_ws_name = "".join(c for c in session.workshop_description if c.isalnum() or c in " _-").strip().replace(" ", "_")[:30]
            filename = f"Certificate_{safe_inst_name}_{cert.id}_{safe_ws_name}.pdf"
            
            cert_pdf_path = os.path.join(_CERTIFICATE_UPLOADS_DIR, filename)

            # Call generate_certificate_pdf
            success = generate_certificate_pdf(
                pdf_path=cert_pdf_path,
                instructor_name=user.name,
                workshop_name=session.workshop_description,
                workshop_date=session.session_date,
                location=session.location
            )
            if success:
                cert.pdf_path = cert_pdf_path
                db.add(cert)
                db.commit()
                pdf_paths.append(cert_pdf_path)
            else:
                print(f"[payments_instructor] Failed to generate certificate PDF for session {session.id}")
        
        # Send email with all certificates
        if pdf_paths:
            email_target = user.email
            if email_target in ["admin@spacepoint.com", "admin@spacepoint.ae"]:
                email_target = "ahmad2012yacine@gmail.com"
            send_certificates_email(to_email=email_target, name=user.name, pdf_paths=pdf_paths)
            
    except Exception as e:
        print(f"[payments_instructor] Certificate generation/emailing failed: {e}")
        import traceback
        traceback.print_exc()

    # Notify admin via email
    try:
        from app.core.config import settings
        # Get admin emails
        from app.models.user import UserRole as UR
        admins = db.query(User).filter(User.role == UR.ADMIN).all()
        for adm in admins:
            email_target = adm.email
            if email_target in ["admin@spacepoint.com", "admin@spacepoint.ae"]:
                email_target = "ahmad2012yacine@gmail.com"
            send_payment_signed_notification_email(
                to_email=email_target,
                instructor_name=user.name,
                portal_url=settings.BASE_URL.rstrip("/") + "/admin"
            )
    except Exception as e:
        print(f"[payments_instructor] Admin notification failed: {e}")

    return {"ok": True, "message": "Letter signed successfully. Thank you!"}


# ══════════════════════════════════════════════════════════════════════════════
# PDF Download (instructor's own signed copy)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/payments/letters/{letter_id}/download")
def download_my_signed_pdf(
    letter_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(_require_instructor)
):
    letter = db.query(PaymentLetter).filter(
        PaymentLetter.id == letter_id,
        PaymentLetter.instructor_user_id == user.id,
        PaymentLetter.is_published == True
    ).first()
    if not letter:
        raise HTTPException(404, "Letter not found")

    path = letter.signed_pdf_path or letter.pdf_path
    if not path or not os.path.exists(path):
        raise HTTPException(404, "PDF not available yet.")

    filename = f"PaymentLetter_{user.name.replace(' ', '_')}_{letter_id}.pdf"
    return FileResponse(path, media_type="application/pdf", filename=filename)


# ══════════════════════════════════════════════════════════════════════════════
# Summary Stats
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/payments/summary")
def get_payments_summary(
    db: Session = Depends(get_db),
    user: User = Depends(_require_instructor)
):
    letters = db.query(PaymentLetter).filter(
        PaymentLetter.instructor_user_id == user.id,
        PaymentLetter.is_published == True
    ).all()

    total_earned = 0.0
    total_hours = 0.0
    total_sessions = 0
    pending_signature = 0

    for letter in letters:
        sess_total = sum(s.compensation_aed for s in letter.sessions)
        addon_total = sum(a.amount_aed for a in letter.addons)
        total_earned += sess_total + addon_total
        total_hours += sum(s.duration_hours for s in letter.sessions)
        total_sessions += len(letter.sessions)
        status_str = letter.status.value if hasattr(letter.status, "value") else letter.status
        if status_str == "PUBLISHED" or status_str == PaymentLetterStatus.PUBLISHED:
            pending_signature += 1

    return {
        "total_earned_aed": round(total_earned, 2),
        "total_hours": round(total_hours, 1),
        "total_sessions": total_sessions,
        "pending_signature": pending_signature,
        "letter_count": len(letters),
    }

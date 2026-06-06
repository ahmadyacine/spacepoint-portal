import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, Enum, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaymentLetterStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    SIGNED = "SIGNED"
    PAID = "PAID"


class SessionRole(str, enum.Enum):
    LEAD_FACILITATOR = "Lead Facilitator"
    FACILITATOR = "Facilitator"
    ASSISTANT_FACILITATOR = "Assistant Facilitator"


# ---------------------------------------------------------------------------
# PaymentBatch — admin grouping tool (e.g. "November 2025 Batch")
# ---------------------------------------------------------------------------
class PaymentBatch(Base):
    __tablename__ = "payment_batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by_admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    letters = relationship("PaymentLetter", back_populates="batch", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# PaymentLetter — one document per instructor (may span multiple sessions)
# ---------------------------------------------------------------------------
class PaymentLetter(Base):
    __tablename__ = "payment_letters"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("payment_batches.id", ondelete="SET NULL"), nullable=True)
    instructor_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    letter_date = Column(String, nullable=True)           # e.g. "17/12/2025"
    reference = Column(String, default="Facilitator Agreement", nullable=True)

    status = Column(Enum(PaymentLetterStatus), default=PaymentLetterStatus.DRAFT, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)

    pdf_path = Column(String, nullable=True)              # unsigned PDF
    signed_pdf_path = Column(String, nullable=True)       # PDF with instructor signature embedded
    instructor_signature_data = Column(Text, nullable=True)  # base64 PNG of canvas signature

    signed_at = Column(DateTime(timezone=True), nullable=True)
    admin_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    batch = relationship("PaymentBatch", back_populates="letters")
    sessions = relationship("PaymentSession", back_populates="letter", cascade="all, delete-orphan", order_by="PaymentSession.sort_order")
    addons = relationship("PaymentAddon", back_populates="letter", cascade="all, delete-orphan", order_by="PaymentAddon.sort_order")


# ---------------------------------------------------------------------------
# PaymentSession — one row in "Schedule of Workshops" table per letter
# ---------------------------------------------------------------------------
class PaymentSession(Base):
    __tablename__ = "payment_sessions"

    id = Column(Integer, primary_key=True, index=True)
    payment_letter_id = Column(Integer, ForeignKey("payment_letters.id", ondelete="CASCADE"), nullable=False, index=True)

    session_date = Column(String, nullable=False)         # "30/10/2025" or date range
    workshop_description = Column(String, nullable=False)
    role = Column(Enum(SessionRole), default=SessionRole.FACILITATOR, nullable=False)
    location = Column(String, nullable=False)
    duration_hours = Column(Float, nullable=False, default=0)
    compensation_aed = Column(Float, nullable=False, default=0)
    sort_order = Column(Integer, default=1, nullable=False)

    letter = relationship("PaymentLetter", back_populates="sessions")


# ---------------------------------------------------------------------------
# PaymentAddon — one row in "Optional Add-ons" table per letter
# ---------------------------------------------------------------------------
class PaymentAddon(Base):
    __tablename__ = "payment_addons"

    id = Column(Integer, primary_key=True, index=True)
    payment_letter_id = Column(Integer, ForeignKey("payment_letters.id", ondelete="CASCADE"), nullable=False, index=True)

    description = Column(String, nullable=False)
    amount_aed = Column(Float, nullable=False, default=0)
    notes = Column(String, nullable=True)
    sort_order = Column(Integer, default=1, nullable=False)

    letter = relationship("PaymentLetter", back_populates="addons")


# ---------------------------------------------------------------------------
# InstructorBankDetails — filled once by instructor from their dashboard
# ---------------------------------------------------------------------------
class InstructorBankDetails(Base):
    __tablename__ = "instructor_bank_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    account_holder_name = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    iban = Column(String, nullable=True)
    swift_bic = Column(String, nullable=True)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ---------------------------------------------------------------------------
# PortalSetting — key/value store for global settings (admin signature, etc.)
# ---------------------------------------------------------------------------
class PortalSetting(Base):
    __tablename__ = "portal_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

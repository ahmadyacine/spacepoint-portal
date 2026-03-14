from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.core.database import Base

class InstructorProfile(Base):
    __tablename__ = "instructor_profiles"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    linkedin_url    = Column(String, nullable=True)
    profile_photo_path  = Column(String, nullable=True)
    instructor_id   = Column(String, unique=True, nullable=True)  # e.g. SP-INS-0001
    issue_date      = Column(DateTime(timezone=True), nullable=True)
    front_card_path = Column(String, nullable=True)
    back_card_path  = Column(String, nullable=True)
    contract_path       = Column(String, nullable=True) # Generated contract (PDF)
    signed_contract_path = Column(String, nullable=True) # Uploaded by instructor
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
